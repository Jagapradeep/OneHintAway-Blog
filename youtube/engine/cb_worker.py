"""Chatterbox voice worker. Runs in its own Python environment (PyTorch, Chatterbox, faster-whisper), separate from
the video engine, because their package versions clash. The engine starts it once and talks to it over stdin/stdout,
one JSON object per line:

  request : {"text": "...", "seed": 3, "out": "/path/take.wav", "ref": "/path/reference.wav",
             "exaggeration": 0.5, "cfg_weight": 0.5}
  answer  : {"sr": 24000, "words": [["Is", 0.12, 0.31, 0.98], ...],  what Whisper heard: start, end, its confidence
             "mos": 4.3, "mos_min": 3.9, "sim": 0.86}

Chatterbox (MIT) says the line copying the reference voice. Three listeners judge each take for the engine:
  Whisper (MIT)             the words, so the engine can check every one
  UTMOS22 strong (MIT)      how natural it sounds, 1 to 5: the whole take ("mos") and its worst 2-second stretch ("mos_min")
  Chatterbox voice encoder  how close the voice is to the reference ("sim", cosine, 1 = same)
Logs go to stderr; stdout carries answers only.
"""
import json, os, sys

import torch, torchaudio as ta

out = sys.stdout
sys.stdout = sys.stderr                     # keep library prints out of the answer channel
torch.set_num_threads(os.cpu_count() or 4)

import numpy as np
from chatterbox.tts import ChatterboxTTS
from faster_whisper import WhisperModel
from speechmos.utmos22.strong.model import UTMOS22Strong

UTMOS_URL = "https://github.com/tarepan/SpeechMOS/releases/download/v1.0.0/utmos22_strong_step7459_v1.pt"
model = ChatterboxTTS.from_pretrained(device="cpu")
ear = WhisperModel(os.environ.get("CB_WHISPER", "small.en"), device="cpu", compute_type="int8")
judge = UTMOS22Strong(); judge.load_state_dict(torch.hub.load_state_dict_from_url(UTMOS_URL, map_location="cpu")); judge.eval()
refs = {}

def naturalness(pcm16):
    """UTMOS of the whole take and of its worst 2-second window (1-second steps), so a short glitch shows."""
    x = torch.from_numpy(pcm16).unsqueeze(0)
    with torch.no_grad():
        whole = float(judge(x, 16000))
        n, w, h = x.shape[1], 32000, 16000
        if n < w + h // 2:
            return whole, whole
        parts = [float(judge(x[:, i:i + w], 16000)) for i in range(0, n - w + 1, h)]
        if (n - w) % h:
            parts.append(float(judge(x[:, n - w:], 16000)))
    return whole, min(parts)

def likeness(pcm16, ref):
    if ref not in refs:
        r, sr = ta.load(ref)
        r = ta.functional.resample(r.mean(0, keepdim=True), sr, 16000)[0].numpy()
        refs[ref] = model.ve.embeds_from_wavs([r], sample_rate=16000)[0]
    e = model.ve.embeds_from_wavs([pcm16], sample_rate=16000)[0]
    return float(np.dot(e, refs[ref]) / (np.linalg.norm(e) * np.linalg.norm(refs[ref]) + 1e-9))
print("chatterbox worker ready", file=sys.stderr, flush=True)
out.write(json.dumps({"ready": True}) + "\n"); out.flush()

for raw in sys.stdin:
    if not raw.strip():
        continue
    req = json.loads(raw)
    try:
        torch.manual_seed(int(req["seed"]))
        wav = model.generate(req["text"], audio_prompt_path=req["ref"],
                             exaggeration=float(req.get("exaggeration", 0.5)), cfg_weight=float(req.get("cfg_weight", 0.5)))
        ta.save(req["out"], wav, model.sr)
        pcm = ta.functional.resample(wav, model.sr, 16000)[0].numpy().astype("float32")
        segs, _ = ear.transcribe(pcm, language="en", word_timestamps=True, beam_size=5, condition_on_previous_text=False,
                                 hotwords=req.get("hotwords") or None)
        words = [[w.word.strip(), round(w.start, 3), round(w.end, 3), round(w.probability, 3)] for s in segs for w in s.words]
        mos, mos_min = naturalness(pcm)
        ans = {"sr": model.sr, "words": words, "mos": round(mos, 3), "mos_min": round(mos_min, 3),
               "sim": round(likeness(pcm, req["ref"]), 3)}
    except Exception as e:                  # report, keep serving
        ans = {"error": f"{type(e).__name__}: {e}"}
    out.write(json.dumps(ans) + "\n"); out.flush()
