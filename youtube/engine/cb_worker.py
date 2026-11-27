"""Chatterbox voice worker. Runs in its own Python environment (PyTorch, Chatterbox, faster-whisper), separate from
the video engine, because their package versions clash. The engine starts it once and talks to it over stdin/stdout,
one JSON object per line:

  request : {"text": "...", "seed": 3, "out": "/path/take.wav", "ref": "/path/reference.wav",
             "exaggeration": 0.5, "cfg_weight": 0.5}
  answer  : {"sr": 24000, "words": [["Is", 0.12, 0.31], ...]}      what Whisper heard, with start and end times

Chatterbox (MIT) says the line copying the reference voice; Whisper (MIT) listens to the take so the engine can
check every word. Logs go to stderr; stdout carries answers only.
"""
import json, os, sys

import torch, torchaudio as ta

out = sys.stdout
sys.stdout = sys.stderr                     # keep library prints out of the answer channel
torch.set_num_threads(os.cpu_count() or 4)

from chatterbox.tts import ChatterboxTTS
from faster_whisper import WhisperModel

model = ChatterboxTTS.from_pretrained(device="cpu")
ear = WhisperModel(os.environ.get("CB_WHISPER", "small.en"), device="cpu", compute_type="int8")
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
        segs, _ = ear.transcribe(pcm, language="en", word_timestamps=True, beam_size=5, condition_on_previous_text=False)
        words = [[w.word.strip(), round(w.start, 3), round(w.end, 3)] for s in segs for w in s.words]
        ans = {"sr": model.sr, "words": words}
    except Exception as e:                  # report, keep serving
        ans = {"error": f"{type(e).__name__}: {e}"}
    out.write(json.dumps(ans) + "\n"); out.flush()
