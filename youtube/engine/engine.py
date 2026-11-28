"""Sample engine for One Hint Away videos: scenes + Kokoro voice + word captions + sound,
rendered frame by frame with Playwright (the post kit's own animation player is embedded)."""
import hashlib, json, math, os, re, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import kitload as K

ROOT = Path(__file__).resolve().parent            # youtube/engine: models/ and .cache/ live here (git-ignored)
CACHE = ROOT / ".cache"; CACHE.mkdir(exist_ok=True)
SR = 48000
if Path("/opt/pw-browsers").exists():
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")

# Same pixels on every run and every machine: software drawing on one thread, fixed colour profile and
# text smoothing, nothing animated by the browser itself (draw(t) sets every frame).
CHROME_ARGS = ["--disable-gpu", "--disable-gpu-rasterization", "--num-raster-threads=1", "--disable-partial-raster",
               "--force-color-profile=srgb", "--font-render-hinting=none", "--disable-lcd-text",
               "--disable-threaded-animation", "--disable-threaded-scrolling", "--disable-skia-runtime-opts"]

# ---------------------------------------------------------------- voice
_kok = None
# tone tags: (speed, pitch shift in semitones, pause before). Kept small: every change below is native to Kokoro
# (its own intonation from punctuation, stress marks in its phonemes, its speed) or a pitch nudge of a few percent,
# never a vocoder rebuild (that distorted the voice on 26 November 2026).
TONES = {"question": (0.95, 0.35, 0.0), "reveal": (0.9, -0.35, 0.5), "lift": (1.05, 0.45, 0.0),
         "warm": (0.94, -0.2, 0.15), "low": (0.93, -0.45, 0.1), "pause": (1.0, 0.0, 0.6)}
_SENT = re.compile(r"(?<=[.?!])\s+")
_MARK = re.compile(r"\[([^\]]+)\]\(/([^/]+)/\)|\*([^*]+)\*")

def _marks(snt):
    """'*word*' stresses a word; '[a](/ˈeɪ/)' gives a word its exact sound (letters, names).
    Returns the plain text and a list of (start, end, phonemes or None for stress)."""
    plain, marks, pos = "", [], 0
    for m in _MARK.finditer(snt):
        plain += snt[pos:m.start()]
        word = m.group(1) or m.group(3)
        marks.append((len(plain), len(plain) + len(word), m.group(2)))
        plain += word; pos = m.end()
    return plain + snt[pos:], marks

def spoken_text(text):
    """What captions show for a voice line: the marks removed."""
    return _MARK.sub(lambda m: m.group(1) or m.group(3), text)

def human(text, voice="af_heart", speed=1.0, tone=None):
    """One narration line as (audio at 48 kHz, [(start, end) per sentence]), from the voice engine in use."""
    if VOICE_ENGINE == "chatterbox":
        return _cb_human(text)
    return _kokoro_human(text, voice, speed, tone)

def _kokoro_human(text, voice="af_heart", speed=1.0, tone=None):
    """One narration line, said sentence by sentence: Kokoro's own intonation from the punctuation, stressed words,
    exact letter sounds, a per-sentence pace and a pitch nudge of at most a few percent, real pauses between
    sentences (longer after a question). Returns (audio, [(start, end) per sentence in seconds])."""
    sp0, st0, _ = TONES.get(tone, (1.0, 0.0, 0.0))
    sents = [x for x in _SENT.split(text.strip()) if x]
    parts, spans, t = [], [], 0.0
    for k, snt in enumerate(sents):
        plain, marks = _marks(snt)
        h = int(hashlib.sha1(plain.encode()).hexdigest()[:6], 16) / 0xFFFFFF
        sp, st = speed * sp0 * (0.975 + 0.05 * h), st0 + (h - 0.5) * 0.3
        if plain.endswith("?"):
            sp *= 0.96; st += 0.3
        elif plain.endswith("!"):
            sp *= 1.04; st += 0.4
        if len(sents) > 1 and k == len(sents) - 1 and plain.endswith("."):
            sp *= 0.97
        a = speak(plain, voice, round(sp, 3), round(2 ** (max(-0.6, min(0.6, st)) / 12), 4), tuple(marks))
        spans.append((t, t + len(a) / SR)); t += len(a) / SR
        parts.append(a)
        if k < len(sents) - 1:
            gap = 0.5 if plain.endswith("?") else (0.42 if plain.endswith("!") else 0.34)
            parts.append(np.zeros(int(gap * SR), np.float32)); t += gap
    return np.concatenate(parts).astype(np.float32), spans

def speak(text, voice="af_heart", speed=1.0, pitch=1.0, marks=()):
    """Kokoro speech at 48 kHz, silence trimmed, cached. marks: (start, end, phonemes or None) from _marks."""
    global _kok
    key = hashlib.sha1(f"{voice}|{speed}|{pitch}|{text}|{marks}|v6".encode()).hexdigest()[:16]
    f = CACHE / f"{key}.wav"
    if not f.exists():
        if _kok is None:
            from kokoro_onnx import Kokoro
            m = ROOT / "models"
            if not (m / "kokoro-v1.0.onnx").exists():
                raise SystemExit("Voice model missing: run the setup step in the yt-video skill (downloads models/ from the kokoro-onnx GitHub release).")
            _kok = Kokoro(str(m / "kokoro-v1.0.onnx"), str(m / "voices-v1.0.bin"))
        rate = speed / pitch
        if marks:                       # build the phonemes piece by piece so each mark lands on its own word
            ph, pos = [], 0
            for a, b, sound in marks:
                if text[pos:a].strip():
                    ph.append(_kok.tokenizer.phonemize(text[pos:a], "en-us"))
                if sound:
                    ph.append(sound)
                else:
                    w = _kok.tokenizer.phonemize(text[a:b], "en-us").replace("ˌ", "ˈ")
                    ph.append(w if "ˈ" in w else "ˈ" + w)
                pos = b
            if text[pos:].strip():
                ph.append(_kok.tokenizer.phonemize(text[pos:], "en-us"))
            s, sr = _kok.create(" ".join(x.strip() for x in ph), voice=voice, speed=rate, lang="en-us", is_phonemes=True)
        else:
            s, sr = _kok.create(text, voice=voice, speed=rate, lang="en-us")
        s = resample_poly(np.asarray(s, dtype=np.float64), SR, sr)
        if pitch != 1.0:                # replay a few percent faster or slower: pitch moves, speed was compensated above
            s = resample_poly(s, 1000, int(round(1000 * pitch)))
        env = np.abs(s) > 0.01
        idx = np.where(env)[0]
        if len(idx):
            s = s[max(0, idx[0] - 480): idx[-1] + 2400]
        sf.write(f, s.astype(np.float32), SR)
    a, _ = sf.read(f, dtype="float32")
    return a

# ---------------------------------------------------------------- voice: Chatterbox (an optional engine)
# Chatterbox (MIT) copies af_heart from a short Kokoro clip and adds expression. Each take is partly random, so every
# line is heard back by Whisper (MIT) and said again with the next seed until Whisper hears exactly the script's
# words. A line that never comes out clean fails the render (VOICE_ERRORS) instead of reaching a video.
VOICE_ENGINE = "kokoro"
VOICE_ERRORS = []
VOICE_NOTES = []       # lines accepted although Whisper heard a word differently: worth one listen
CB = {"exaggeration": 0.5, "cfg_weight": 0.5, "chatterbox": "ab55923", "whisper": "small.en", "judge": "utmos22-strong",
      "tries": 8,              # takes per line before the render fails (hard faults: words, noise, clipping, long gaps)
      "soft_tries": 3,         # takes with the right words but below the quality bar before keeping the best of them
      "gap_max": 0.8,          # longest silence inside a sentence, seconds
      "rate": (1.6, 4.6),      # words a second for a line of four words or more
      "mos_min": 3.8,          # UTMOS of the whole take (clean Kokoro scores about 4.4; a glitch drops it by about 1)
      "mos_window_min": 3.4,   # UTMOS of the worst 2-second stretch
      "sim_min": 0.75,         # likeness to the af_heart reference (cosine of voice-encoder embeddings)
      "speech_rms": 0.075}     # every line is levelled to this loudness of speech
LAST_META = {}
CB_REF_TEXT = ("Here is the idea in one line. We keep a small notebook of the numbers we have already seen. "
               "For each new number, we check the notebook first. That one habit turns a slow search into a fast one.")
_cb = None

def set_voice_engine(name):
    global VOICE_ENGINE
    if name not in ("kokoro", "chatterbox"):
        raise SystemExit(f"unknown voice engine {name!r}: use kokoro or chatterbox")
    VOICE_ENGINE = name

_ONES = ("zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
         "seventeen eighteen nineteen").split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()

def _num(n):
    if n < 20:
        return _ONES[n]
    if n < 100:
        return _TENS[n // 10] + ("" if n % 10 == 0 else " " + _ONES[n % 10])
    if n < 1000:
        return _ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + _num(n % 100))
    if n < 1_000_000:
        return _num(n // 1000) + " thousand" + ("" if n % 1000 == 0 else " " + _num(n % 1000))
    return " ".join(_ONES[int(d)] for d in str(n))

def norm_words(text):
    """Words to compare what was meant with what Whisper heard: lower case, numbers as words, no punctuation.
    Every word counts (an extra "and" is an extra word); only the "and" inside a number ("a hundred and two") is dropped."""
    t = re.sub(r"(?<=\d),(?=\d{3})", "", text.lower().replace("’", "'"))
    t = re.sub(r"\d+", lambda m: " " + _num(int(m.group())) + " ", t)
    t = re.sub(r"\b(hundred|thousand) and\b", r"\1", t)
    t = re.sub(r"(?<=[a-z0-9])\.(?=[a-z])", " dot ", t)          # onehintaway.com is said "one hint away dot com"
    return re.findall(r"[a-z]+", t.replace("'", ""))

_tok = None

def _phones(words):
    """How words sound (espeak, as Kokoro uses), without stress, spaces or the small vowel differences."""
    global _tok
    if _tok is None:
        from kokoro_onnx.tokenizer import Tokenizer
        _tok = Tokenizer()
    p = _tok.phonemize(" ".join(words), "en-us") if words else ""
    return re.sub(r"[ˈˌ\s]", "", p).replace("ɐ", "ə").replace("ɚ", "əɹ")

def _edits(a, b):
    row = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, row[0] = row[0], i
        for j, y in enumerate(b, 1):
            prev, row[j] = row[j], min(row[j] + 1, row[j - 1] + 1, prev + (x != y))
    return row[-1]

def sound_alike(exp, heard):
    """Whisper wrote the right sounds in other words ("Two Sum" as "twosome", "seen" as "scene")?
    Every differing stretch must sound the same, give or take one sound in five; an extra or missing word never passes.
    Returns (True, "how Whisper spelled it") or (False, "")."""
    from difflib import SequenceMatcher
    notes = []
    for op, i0, i1, j0, j1 in SequenceMatcher(None, exp, heard, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        if i0 == i1 or j0 == j1:
            return False, ""
        a, b = _phones(exp[i0:i1]), _phones(heard[j0:j1])
        if _edits(a, b) > max(1, int(0.2 * max(len(a), len(b)))):
            return False, ""
        notes.append(f"{' '.join(exp[i0:i1])!r} written as {' '.join(heard[j0:j1])!r}")
    return True, "; ".join(notes)

def _cb_text(text):
    """What Chatterbox reads: marks removed, a marked single letter in quotes so it is said as a letter."""
    return _MARK.sub(lambda m: f'"{m.group(1)}"' if m.group(1) and len(m.group(1)) == 1 else (m.group(1) or m.group(3)), text)

def _cb_ref():
    f = CACHE / "cb-reference-af_heart.wav"
    if not f.exists():
        a, _ = _kokoro_human(CB_REF_TEXT)
        sf.write(f, a, SR)
    return f

def _cb_ask(req):
    global _cb
    if _cb is None:
        py = os.environ.get("CB_PYTHON")
        if not py:
            raise SystemExit("The Chatterbox voice needs CB_PYTHON: the python of the Chatterbox environment (the videos workflow sets it up).")
        _cb = subprocess.Popen([py, "-u", str(ROOT / "cb_worker.py")], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                               env={**os.environ, "CB_WHISPER": CB["whisper"]})
        if not json.loads(_cb.stdout.readline() or "{}").get("ready"):
            raise SystemExit("The Chatterbox worker did not start (see the log above).")
    _cb.stdin.write(json.dumps(req) + "\n"); _cb.stdin.flush()
    line = _cb.stdout.readline()
    if not line:
        raise SystemExit("The Chatterbox worker stopped (see the log above).")
    return json.loads(line)

def _cb_junk(a, sr, words):
    """Sound well after the last word or well before the first (a breath is fine, a mumble is not)."""
    if not words:
        return True
    hop = int(0.02 * sr); n = len(a) // hop
    loud = np.sqrt(np.mean(a[: n * hop].reshape(n, hop) ** 2, axis=1)) > 0.02 * max(1e-6, np.abs(a).max()) * 2
    head = loud[: max(0, int((words[0][1] - 0.35) / 0.02))].sum() * 0.02
    tail = loud[int((words[-1][2] + 0.35) / 0.02):].sum() * 0.02
    return head > 0.4 or tail > 0.4

def _gap_after(sentence):
    """Pause after a sentence, as Kokoro makes it: a question gets the longest, a statement the shortest."""
    p = sentence.rstrip()[-1:] if sentence.strip() else "."
    return 0.5 if p == "?" else (0.42 if p == "!" else 0.34)

def _cb_shape(a, sr, heard, text, n_exp):
    """Trim the take to its words, cut it between sentences at the quietest point, and make each pause at least
    as long as Kokoro's (Chatterbox runs sentences together). Returns (audio at 48 kHz, sentence spans)."""
    a = a.astype(np.float64)
    if not heard:
        return resample_poly(a, SR, sr).astype(np.float32), [(0.0, len(a) / sr)]
    sents = [x for x in _SENT.split(text.strip()) if x]
    counts = [len(norm_words(x)) for x in sents]
    scale = len(heard) / max(1, n_exp)
    rng, i = [], 0                                  # first and last heard word of each sentence
    for c in counts:
        j0 = min(len(heard) - 1, int(round(i * scale)))
        j1 = min(len(heard) - 1, max(j0, int(round((i + c) * scale)) - 1))
        rng.append((j0, j1)); i += c
    # where the voice really starts and stops: Whisper's first and last word times are approximate (often early),
    # so find the first and last loud 10 ms around them; breaths and room tone before or after are cut
    fr = max(1, int(0.01 * sr)); nf = len(a) // fr
    lvl = np.sqrt((a[: nf * fr].reshape(nf, fr) ** 2).mean(axis=1)) if nf else np.zeros(1)
    loud = np.flatnonzero(lvl > 0.15 * (lvl.max() + 1e-9))
    lo = int(max(0.0, heard[0][1] - 0.4) / 0.01); hi = int((heard[-1][2] + 0.6) / 0.01)
    inside = loud[(loud >= lo) & (loud <= hi)]
    if len(inside):
        start = max(0.0, inside[0] * 0.01 - 0.05); end = min(len(a) / sr, (inside[-1] + 1) * 0.01 + 0.12)
    else:
        start = max(0.0, heard[0][1] - 0.12); end = min(len(a) / sr, heard[-1][2] + 0.3)
    hop = max(1, int(0.01 * sr))
    def quietest(lo, hi):
        lo, hi = max(start, lo), min(end, max(lo + 0.01, hi))
        k0, k1 = int(lo * sr), int(hi * sr)
        if k1 - k0 < hop:
            return (lo + hi) / 2
        seg = a[k0:k1]; n = len(seg) // hop
        e = (seg[: n * hop].reshape(n, hop) ** 2).mean(axis=1)
        return (k0 + (int(np.argmin(e)) + 0.5) * hop) / sr
    cuts = [start]
    for (_, j1), (j0n, _) in zip(rng, rng[1:]):
        cuts.append(quietest(heard[j1][2] - 0.05, heard[j0n][1] + 0.05))
    cuts.append(end)
    fade = int(0.006 * sr); out, spans, t = [], [], 0.0
    for k, (c0, c1) in enumerate(zip(cuts, cuts[1:])):
        piece = a[int(c0 * sr): int(c1 * sr)].copy()
        if len(piece) > 2 * fade:
            if k:
                piece[:fade] *= np.linspace(0, 1, fade)
            piece[-fade:] *= np.linspace(1, 0, fade)
        j0, j1 = rng[k]
        spans.append((round(t + max(0.0, heard[j0][1] - c0), 3), round(t + min(c1, heard[j1][2]) - c0, 3)))
        out.append(piece); t += len(piece) / sr
        if k < len(sents) - 1:                       # top the natural pause up to Kokoro's
            natural = max(0.0, heard[rng[k + 1][0]][1] - heard[j1][2])
            add = max(0.0, _gap_after(sents[k]) - natural)
            out.append(np.zeros(int(add * sr))); t += add
    a = resample_poly(np.concatenate(out), SR, sr).astype(np.float32)
    f2 = min(len(a), int(0.03 * SR)); a[-f2:] *= np.linspace(1, 0, f2, dtype=np.float32)
    hop = int(0.02 * SR); n = len(a) // hop                     # level the line: the same speech loudness every time
    if n:
        r = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(axis=1)); speech = r[r > 0.1 * r.max()]
        if len(speech):
            g = CB["speech_rms"] / max(1e-6, float(np.sqrt((speech ** 2).mean())))
            a = a * min(g, 0.95 / max(1e-6, float(np.abs(a).max())))
    return a.astype(np.float32), spans

def _cb_gates(t, exp, sents_end):
    """Judge one take. Hard faults are never shipped; soft faults send it back for another take."""
    hard, soft, words = [], [], t["words"]
    hw = [h[0] for h in t["heard"]]
    if hw != exp:
        same, how = sound_alike(exp, hw)
        if same:
            t["spelled"] = how                     # the voice said the words; Whisper spelled them its own way
        else:
            hard.append("words differ")
    if t["junk"]:
        hard.append("sound before or after the words")
    if t["peak"] >= 0.999:
        hard.append("clipped")
    for (w0, _, e0), (_, s1, _) in zip(words, words[1:]):
        if s1 - e0 > CB["gap_max"] and not w0.rstrip().endswith(sents_end):
            hard.append(f"{s1 - e0:.1f} s silence after {w0.strip()!r}"); break
    span = (words[-1][2] - words[0][1]) if words else 0.0     # first word to last, natural pauses included
    rate = len(exp) / max(span, 0.3)
    t["rate"] = round(rate, 2)
    if len(exp) >= 4 and not CB["rate"][0] <= rate <= CB["rate"][1]:
        soft.append(f"{rate:.1f} words a second")
    if t["mos"] < CB["mos_min"]:
        soft.append(f"naturalness {t['mos']:.2f}")
    if t["mos_min"] < CB["mos_window_min"]:
        soft.append(f"a rough stretch ({t['mos_min']:.2f})")
    if t["vsim"] < CB["sim_min"]:
        soft.append(f"voice likeness {t['vsim']:.2f}")
    return hard, soft

def _tight(a, spans, keep_in=0.05, keep_out=0.12):
    """Cut quiet lead-in and tail (breaths, room tone) from a finished 48 kHz line and move its spans to match."""
    fr = int(0.01 * SR); nf = len(a) // fr
    if not nf:
        return a, spans
    lvl = np.sqrt((a[: nf * fr].reshape(nf, fr) ** 2).mean(axis=1)); loud = np.flatnonzero(lvl > 0.15 * (lvl.max() + 1e-9))
    if not len(loud):
        return a, spans
    s0 = max(0.0, loud[0] * 0.01 - keep_in); s1 = min(len(a) / SR, (loud[-1] + 1) * 0.01 + keep_out)
    if s0 < 0.02 and len(a) / SR - s1 < 0.02:
        return a, spans
    a = a[int(s0 * SR): int(s1 * SR)].copy(); d = len(a) / SR
    f = min(len(a), int(0.02 * SR)); a[-f:] *= np.linspace(1, 0, f, dtype=np.float32)
    return a, [(round(max(0.0, x - s0), 3), round(min(d, y - s0), 3)) for x, y in spans]

def _cb_human(text):
    """One line from Chatterbox, judged by four checks (words, timing, naturalness, likeness to af_heart), cached.
    Returns (audio, sentence spans). LAST_META describes the take for the video's listen list."""
    global LAST_META
    said = _cb_text(text); exp = norm_words(spoken_text(text)); spoken = spoken_text(text)
    key = hashlib.sha1(f"cb|{said}|{sorted((k, str(v)) for k, v in CB.items())}|v3".encode()).hexdigest()[:16]
    fa, fj = CACHE / f"cb-{key}.wav", CACHE / f"cb-{key}.json"
    if fa.exists() and fj.exists():
        a, _ = sf.read(fa, dtype="float32"); meta = json.loads(fj.read_text())
        LAST_META = {**meta, "text": spoken}
        if meta.get("note"):
            VOICE_NOTES.append(f"{spoken!r}: {meta['note']}")
        return _tight(a, [tuple(x) for x in meta["spans"]])       # lines saved before the loudness trim get it too
    from difflib import SequenceMatcher
    ref, takes, pick, note = _cb_ref(), [], None, ""
    for seed in range(1, CB["tries"] + 1):
        tmp = CACHE / f"cb-{key}-take{seed}.wav"
        ans = _cb_ask({"text": said, "seed": seed, "out": str(tmp), "ref": str(ref),
                       "exaggeration": CB["exaggeration"], "cfg_weight": CB["cfg_weight"]})
        if "error" in ans:
            print(f"   chatterbox take {seed} failed: {ans['error']}", flush=True); continue
        a, sr = sf.read(tmp, dtype="float32"); tmp.unlink(missing_ok=True)
        if a.ndim > 1:
            a = a.mean(axis=1)
        heard = []
        for w, s0, s1 in ans["words"]:
            heard += [(x, s0, s1) for x in norm_words(w)]
        hw = [h[0] for h in heard]
        t = {"seed": seed, "a": a, "sr": sr, "heard": heard, "words": ans["words"], "junk": _cb_junk(a, sr, ans["words"]),
             "peak": float(np.abs(a).max()) if len(a) else 0.0, "mos": ans.get("mos", 5.0), "mos_min": ans.get("mos_min", 5.0),
             "vsim": ans.get("sim", 1.0), "match": SequenceMatcher(None, exp, hw).ratio(),
             "text": " ".join(w[0] for w in ans["words"])}
        t["hard"], t["soft"] = _cb_gates(t, exp, (".", "?", "!", ":", ";"))
        takes.append(t)
        print(f"   take {seed}: " + ("ok" if not t["hard"] + t["soft"] else "; ".join(t["hard"] + t["soft"]))
              + f" | mos {t['mos']:.2f}/{t['mos_min']:.2f} likeness {t['vsim']:.2f}", flush=True)
        if not t["hard"] and not t["soft"]:
            pick = t; break
        sound = [x for x in takes if not x["hard"]]
        if len(sound) >= CB["soft_tries"]:            # the words are right but it is below the bar every time: keep the best
            pick = max(sound, key=lambda x: (x["mos_min"], x["mos"], x["vsim"]))
            note = (note + "; " if note else "") + "below the quality bar: " + "; ".join(pick["soft"]); break
    accepted = pick is not None
    if pick is None:
        best = max(takes, key=lambda x: (len(x["hard"]) == 1, x["match"], x["mos_min"])) if takes else None
        VOICE_ERRORS.append(f"Chatterbox could not say this line cleanly in {CB['tries']} takes, reword it: {spoken!r}"
                            + (f" (closest take: {'; '.join(best['hard'])}; heard {best['text']!r})" if best else ""))
        LAST_META = {"text": spoken, "failed": True}
        if not best:
            return np.zeros(int(SR), np.float32), [(0.0, 1.0)]
        pick = best
    a, spans = _cb_shape(pick["a"], pick["sr"], pick["heard"], spoken, len(exp))
    meta = {"spans": spans, "seed": pick["seed"], "takes": len(takes), "heard": pick["text"], "note": note,
            "mos": pick["mos"], "mos_min": pick["mos_min"], "likeness": pick["vsim"], "rate": pick.get("rate"),
            "spelled": pick.get("spelled", "")}
    LAST_META = {**meta, "text": spoken}
    if note:
        VOICE_NOTES.append(f"{spoken!r}: {note}")
    if accepted:                                  # a failed line is never cached, so the next run tries it again
        sf.write(fa, a, SR); fj.write_text(json.dumps(meta))
    print(f"   chatterbox: take {pick['seed']} of {len(takes)} for {spoken[:50]!r}" + (f" ({note})" if note else ""), flush=True)
    return a, spans

def _syl(w):
    w = re.sub(r"[^a-z0-9]", "", w.lower())
    if not w:
        return 0.5
    if w.isdigit():
        return 1.2 * len(w)
    return max(1, len(re.findall(r"[aeiouy]+", w)) - (1 if w.endswith("e") and len(w) > 3 else 0))

def word_times(show, t0, dur):
    words = show.split()
    wts = []
    for w in words:
        p = 0.9 if w[-1] in ".?!:" else 0.45 if w[-1] in ",;" else 0
        wts.append(_syl(w) + 0.35 + p)
    tot = sum(wts)
    out, t = [], t0
    for w, x in zip(words, wts):
        out.append({"w": w, "t": round(t, 3)})
        t += dur * x / tot
    return out

# ---------------------------------------------------------------- sound
def _env(n, a=0.004, d=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / a)
    if d:
        e *= np.exp(-t / d)
    return e

def tone(f, dur, decay, vol, harm=0.15):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + harm * np.sin(4 * np.pi * f * t)
    return (s * _env(n, d=decay) * vol).astype(np.float32)

def whoosh(dur=0.45, vol=0.22):
    n = int(dur * SR); rng = np.random.default_rng(7)
    x = rng.standard_normal(n)
    k = 24; lp = np.convolve(x, np.ones(k) / k, mode="same")
    bp = lp - np.convolve(lp, np.ones(200) / 200, mode="same")
    t = np.linspace(0, 1, n); e = np.sin(np.pi * t) ** 2
    return (bp / (np.abs(bp).max() + 1e-9) * e * vol).astype(np.float32)

def marimba(f, dur=0.6, vol=0.12):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.22) + 0.25 * np.sin(2 * np.pi * f * 3.98 * t) * np.exp(-t / 0.05)
    return (s * np.minimum(1, t / 0.006) * vol).astype(np.float32)

def sfx(kind):
    if kind == "turn":
        a = marimba(392.0); b = marimba(587.33, vol=0.10)
        out = np.zeros(int(0.75 * SR), np.float32); out[:len(a)] += a; o = int(0.07 * SR); out[o:o + len(b)] += b
        return out
    if kind == "tick": return tone(1700, 0.05, 0.012, 0.16)
    if kind == "land": return tone(620, 0.09, 0.03, 0.13, harm=0.4)
    if kind == "count": return tone(1046, 0.16, 0.05, 0.22)
    if kind == "go": return tone(1568, 0.5, 0.16, 0.24)
    if kind == "pop":
        a = tone(880, 0.16, 0.05, 0.2); b = tone(1318, 0.2, 0.07, 0.2)
        out = np.zeros(int(0.3 * SR), np.float32); out[:len(a)] += a; o = int(0.06 * SR); out[o:o + len(b)] += b
        return out
    if kind == "chime":
        out = np.zeros(int(1.4 * SR), np.float32)
        for i, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
            s = tone(f, 1.0, 0.35, 0.16); o = int(i * 0.08 * SR); out[o:o + len(s)] += s
        return out
    raise ValueError(kind)

def music(dur, bpm=96, vol=0.05):
    """Soft generated bed (Am F C G pad + quiet plucks). No licensing involved."""
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (130.81, 164.81, 196.0), (196.0, 246.94, 293.66)]
    bar = 4 * 60 / bpm * 2
    for k in range(int(dur / bar) + 1):
        c = chords[k % 4]; s0 = int(k * bar * SR); s1 = min(n, int((k + 1) * bar * SR) + int(0.6 * SR))
        if s0 >= n: break
        tt = np.arange(s1 - s0) / SR
        e = np.minimum(1, tt / 0.9) * np.minimum(1, np.maximum(0, (bar + 0.6 - tt) / 0.9))
        for f in c:
            out[s0:s1] += (np.sin(2 * np.pi * f * tt) * 0.5 + np.sin(2 * np.pi * f * 2.003 * tt) * 0.12) * e * 0.33
        step = 60 / bpm / 2
        for j in range(int(bar / step)):
            f = c[j % 3] * 2; p0 = s0 + int(j * step * SR)
            pl = tone(f, 0.35, 0.09, 0.22, harm=0.05)
            if p0 + len(pl) < n: out[p0:p0 + len(pl)] += pl
    return out / (np.abs(out).max() + 1e-9) * vol

# ---------------------------------------------------------------- timeline
class Video:
    def __init__(self, name, W, H, fps=30, voice="af_heart", speed=1.0, cap_chars=28):
        self.name, self.W, self.H, self.fps = name, W, H, fps
        self.voice, self.speed, self.cap_chars = voice, speed, cap_chars
        self.t = 0.0
        self.scenes, self.clips, self.caps, self.fx, self.extra = [], [], [], [], {}

    def _line(self, line, at):
        if isinstance(line, str):
            line = {"say": line}
        say = line["say"]; show = line.get("show", say)
        a, spans = human(say, self.voice, self.speed, line.get("tone"))
        if VOICE_ENGINE == "chatterbox":           # what the listen list needs: where the line is and how it scored
            self.__dict__.setdefault("voice_log", []).append({"t": round(at, 2), **LAST_META})
        show = spoken_text(show)
        d = len(a) / SR
        self.clips.append((at, a))
        shows = [x for x in _SENT.split(show.strip()) if x]
        if len(shows) == len(spans):          # time the captions sentence by sentence, so pauses line up
            words = []
            for txt, (a0, a1) in zip(shows, spans):
                words += word_times(txt, at + a0, a1 - a0)
        else:
            words = word_times(show, at, d)
        # captions: one whole sentence per caption, never cut inside a sentence
        chunk = []
        for w in words:
            chunk.append(w)
            if w["w"][-1] in ".?!":
                self.caps.append({"t0": chunk[0]["t"], "words": chunk}); chunk = []
        if chunk:
            self.caps.append({"t0": chunk[0]["t"], "words": chunk})
        self.caps[-1]["end"] = at + d
        return d

    def scene(self, sid, lines=(), pre=0.35, gap=0.22, post=0.45, countdown=0, min_dur=0, fx_in="turn", cd_step=1.0, holds=None, **data):
        """holds: {line index: seconds} - an animation that starts on that line runs this long,
        so the next line waits for it instead of cutting it off."""
        holds = holds or {}
        t0 = self.t
        cues, t = {}, t0 + pre
        if fx_in:
            self.fx.append((t0, fx_in))
        for i, ln in enumerate(lines):
            if isinstance(ln, dict) and ln.get("wait"):
                t += ln["wait"]; continue
            if isinstance(ln, dict) and ln.get("think"):       # silent thinking time with a visible timer (cue T<i>)
                cues[f"T{i}"] = round(t - t0, 3); t += ln["think"]; continue
            if isinstance(ln, dict) and ln.get("tone"):
                t += TONES[ln["tone"]][2]
            cues[f"L{i}"] = round(t - t0, 3); start = t
            t += self._line(ln, t) + (ln.get("gap", gap) if isinstance(ln, dict) else gap)
            if i in holds:
                t = max(t, start + holds[i])
        if countdown:
            cues["count"] = round(t - t0, 3)
            for k in range(countdown):
                self.fx.append((t + k * cd_step, "count"))
            self.fx.append((t + countdown * cd_step, "go"))
            t += countdown * cd_step + 0.45
        t1 = max(t + post - gap, t0 + min_dur)
        self.scenes.append(dict(id=sid, t0=round(t0, 3), t1=round(t1, 3), cues=cues, **data))
        self.t = t1
        return self.scenes[-1]

    def kit_scene(self, sid, tl, narr, pre=0.5, post=0.6, slow=1.0, land_fx=True, **data):
        """The post's own animation, re-timed so every narrated step holds until its line ends."""
        S = tl["states"]
        clips = {k: (v if isinstance(v, dict) else {"say": v}) for k, v in narr.items()}
        durs = {k: len(human(c["say"], self.voice, self.speed, c.get("tone"))[0]) / SR for k, c in clips.items()}
        t = 0.0
        for k, s in enumerate(S):
            ln = s["len"] * slow
            if k in durs:
                ln = max(ln, s["mv"] * 0.35 + durs[k] + 0.3)
            s["t0"], s["len"] = round(t, 3), round(ln, 3)
            t += ln
        tl["duration"] = round(t + tl["T"]["FADE"], 3)
        end = t - 0.01
        t0 = self.t
        self.fx.append((t0, "turn"))
        for k, s in enumerate(S):
            at = t0 + pre + s["t0"]
            if land_fx and k:
                self.fx.append((at + s["mv"] * 0.85, "land"))
            if k in clips:
                self._line(clips[k], at + s["mv"] * 0.35)
        self.fx.append((t0 + pre + S[-1]["t0"] + S[-1]["mv"], "chime"))
        t1 = t0 + pre + end + post
        self.scenes.append(dict(id=sid, t0=round(t0, 3), t1=round(t1, 3), cues={}, kit={"pre": pre, "end": round(end, 3)}, **data))
        self.t = t1
        return self.scenes[-1]

    # ------------------------------------------------------------ audio
    def mix(self, path, music_vol=0.05):
        dur = self.t + 0.2
        n = int(dur * SR)
        voice = np.zeros(n, np.float32); fx = np.zeros(n, np.float32)
        for at, a in self.clips:
            i = int(at * SR); voice[i:i + len(a)] += a[: max(0, n - i)]
        self.fx_dropped = []
        for at, k in self.fx:
            s = sfx(k); i = int(at * SR)
            # a scene-change note needs the voice right behind it; alone in a quiet stretch it sounds like a click
            # or a mic being switched off (27 and 28 Nov 2026, before "Thanks for watching.")
            if k == "turn" and not np.abs(voice[i: i + int(0.8 * SR)]).max(initial=0) > 0.02:
                self.fx_dropped.append(round(at, 2)); continue
            if i < n: fx[i:i + len(s)] += s[: n - i]
        bed = music(dur, vol=music_vol) if music_vol else np.zeros(n, np.float32)
        # duck the bed under the voice
        env = np.convolve(np.abs(voice), np.ones(4800) / 4800, mode="same")
        duck = 1 - 0.55 * np.clip(env / 0.03, 0, 1)
        bed = bed * np.convolve(duck, np.ones(9600) / 9600, mode="same")
        mixd = voice * 0.9 + fx + bed
        mixd = mixd / (np.abs(mixd).max() + 1e-9) * 0.5          # headroom before loudness is set
        sf.write(str(path), np.stack([mixd, mixd], 1), SR)

    # ------------------------------------------------------------ render
    def data(self):
        return {"W": self.W, "H": self.H, "dur": round(self.t, 3), "scenes": self.scenes, "caps": self.caps, **self.extra}

    def render(self, page_html, out_dir, draft=False, frames=None):
        from playwright.sync_api import sync_playwright
        out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
        html_path = out_dir / f"{self.name}.html"
        html_path.write_text(page_html)
        wav = out_dir / f"{self.name}.wav"; self.mix(wav, music_vol=self.extra.get("music", 0.05))
        silent = out_dir / f"{self.name}-silent.mp4"
        fps = self.fps
        with sync_playwright() as p:
            br = p.chromium.launch(args=CHROME_ARGS)
            pg = br.new_page(viewport={"width": self.W, "height": self.H})
            pg.set_content(page_html); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            pg.evaluate("window.fitCode && window.fitCode()")
            if frames is not None:           # stills only, for checking
                for t in frames:
                    pg.evaluate(f"window.draw({t})")
                    pg.screenshot(path=str(out_dir / f"{self.name}-{t:06.2f}.png"))
                br.close(); return None
            nfr = int(math.ceil(self.t * fps))
            ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "png", "-i", "-",
                                   "-c:v", "libx264", "-preset", "veryfast" if draft else "medium", "-crf", "20" if draft else "16",
                                   "-pix_fmt", "yuv420p", "-threads", "1", "-r", str(fps), str(silent)], stdin=subprocess.PIPE)
            for i in range(nfr):
                pg.evaluate(f"window.draw({i / fps})")
                ff.stdin.write(pg.screenshot(type="png"))
            ff.stdin.close(); ff.wait(); br.close()
        final = out_dir / f"{self.name}.mp4"
        # loudness in two measured passes, then a limiter: never louder than -1.6 dBFS, so nothing clips
        meas = subprocess.run(["ffmpeg", "-nostats", "-i", str(wav), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                               "-f", "null", "-"], capture_output=True, text=True).stderr
        mj = json.loads(meas[meas.rindex("{"): meas.rindex("}") + 1])
        ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={mj['input_i']}:measured_TP={mj['input_tp']}:"
              f"measured_LRA={mj['input_lra']}:measured_thresh={mj['input_thresh']}:offset={mj['target_offset']}:linear=true,"
              "alimiter=limit=0.83:level=disabled:attack=5:release=50")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                        "-af", ln, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        "-shortest", "-movflags", "+faststart", str(final)], check=True)
        silent.unlink()
        return final

    def srt(self, path):
        def ts(x):
            h, r = divmod(x, 3600); m, s = divmod(r, 60)
            return f"{int(h):02}:{int(m):02}:{int(s):02},{int(round((s - int(s)) * 1000)):03}"
        out = []
        for i, c in enumerate(self.caps):
            end = c.get("end") or (self.caps[i + 1]["t0"] if i + 1 < len(self.caps) else self.t)
            out.append(f"{i + 1}\n{ts(c['t0'])} --> {ts(end)}\n{' '.join(w['w'] for w in c['words'])}\n")
        Path(path).write_text("\n".join(out))

# ---------------------------------------------------------------- page JS
ENGINE_JS = r"""
(function(){
const D = window.__D;
const cl = x => Math.min(1, Math.max(0, x));
const sm = x => { x = cl(x); return x*x*(3-2*x); };
const back = x => { x = cl(x); const c = 1.6; return 1 + (c+1)*Math.pow(x-1,3) + c*Math.pow(x-1,2); };
const scenes = D.scenes.map(s => ({...s, el: document.getElementById('sc_' + s.id)}));
for (const s of scenes) s.items = s.el ? [...s.el.querySelectorAll('[data-at]')] : [];
const capEl = document.getElementById('caps') || document.createElement('div');
const prog = document.getElementById('prog');
const kitwrap = document.getElementById('kitwrap');
let lastCap = -1;
function cueT(s, v){ if (v === undefined || v === null || v === '') return 0; const n = Number(v); if (!isNaN(n)) return n;
  const m = /^([A-Za-z0-9]+)([+-][0-9.]+)?$/.exec(v); const base = s.cues[m[1]]; return (base === undefined ? 0 : base) + (m[2] ? Number(m[2]) : 0); }
window.draw = function(t){
  if (prog) prog.style.width = (100 * cl(t / D.dur)) + '%';
  let kitShown = false;
  for (const s of scenes) {
    if (!s.el) continue;
    const local = t - s.t0, dur = s.t1 - s.t0;
    const fin = s.cut ? 1 : sm(local / 0.35), fout = s.hold ? 1 : sm((s.t1 - t) / 0.3);
    const on = t >= s.t0 && t < s.t1 + (s.hold ? 1e9 : 0);
    const op = on ? Math.min(fin, fout) : 0;
    s.el.style.opacity = op; s.el.style.visibility = op > 0.001 ? 'visible' : 'hidden';
    s.el.style.transform = `translateY(${(1 - fin) * 26}px)`;
    if (!on) continue;
    for (const it of s.items) {
      const a = cueT(s, it.dataset.at), e = (local - a) / 0.5;
      const end = it.dataset.until !== undefined ? cueT(s, it.dataset.until) : 1e9;
      const eo = sm((end - local) / 0.3);
      it.style.opacity = Math.min(sm(e * 1.6), eo);
      const kind = it.dataset.fx || 'rise';
      if (kind === 'pop') it.style.transform = `scale(${0.7 + 0.3 * back(e)})`;
      else if (kind === 'none') it.style.transform = 'none';
      else it.style.transform = `translateY(${(1 - back(e)) * 34}px)`;
    }
    if (s.kit && kitwrap) {
      kitShown = true;
      kitwrap.style.opacity = op;
      const k = s.kit; kitwrap.style.transform = `translate(${k.x}px, ${k.y + (1 - fin) * 26}px) scale(${k.scale})`;
      const kt = Math.max(0, Math.min(k.end, (local - k.pre) * (k.speed || 1)));
      window.kitDraw(kt);
    }
    if (s.onDraw && window[s.onDraw]) window[s.onDraw](local, s, t);
  }
  if (kitwrap && !kitShown) kitwrap.style.opacity = 0;
  if (window.drawExtra) window.drawExtra(t);
  if (window.drawViz) window.drawViz(t);
  // captions
  let ci = -1;
  for (let i = 0; i < D.caps.length; i++) { const c = D.caps[i]; const end = c.end !== undefined ? c.end + 0.25 : (i + 1 < D.caps.length ? D.caps[i+1].t0 : D.dur);
    if (t >= c.t0 - 0.05 && t < end) { ci = i; break; } }
  if (ci !== lastCap) { lastCap = ci; capEl.innerHTML = ci < 0 ? '' : D.caps[ci].words.map(w => `<span class="w${/[<>=]/.test(w.w) ? ' code' : ''}">${w.w.replace(/&/g,'&amp;').replace(/</g,'&lt;')}</span>`).join(' '); }
  if (ci >= 0) { const c = D.caps[ci], sp = capEl.children; let cur = -1;
    for (let j = 0; j < c.words.length; j++) if (t >= c.words[j].t) cur = j;
    for (let j = 0; j < sp.length; j++) { sp[j].classList.toggle('now', j === cur); sp[j].classList.toggle('said', j < cur); }
    capEl.style.opacity = sm((t - c.t0 + 0.05) / 0.12); }
};
})();
"""

def page(W, H, body, css, d, kit_v=None, kit_tl=None, extra_js=""):
    kit = ""
    if kit_tl is not None:
        js = K.kit_player_js().replace("const capA = capLayer(), capB = capLayer();",
                                       "const capA = capLayer(), capB = capLayer(); capA.style.display='none'; capB.style.display='none';")
        kit = "<script>window.__TL=" + json.dumps(kit_tl) + ";</script><script>" + js + "</script>"
    return ("<!doctype html><html><head><meta charset='utf-8'><style>" + K.FONT_CSS +
            f"html,body{{margin:0;background:#08090B;width:{W}px;height:{H}px;overflow:hidden}}" + css + "</style></head><body>" + body +
            kit + "<script>window.__D=" + json.dumps(d) + ";</script><script>" + extra_js + "</script><script>" + ENGINE_JS + "</script></body></html>")
