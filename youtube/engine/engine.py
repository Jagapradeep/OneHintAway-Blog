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
# words. A line that never comes out clean is said by Kokoro instead (listed in the listen list): no doubtful take ships
# and no voice problem stops a render. VOICE_ERRORS stays empty unless a future check needs to stop one.
VOICE_ENGINE = "kokoro"
VOICE_ERRORS = []
VOICE_NOTES = []       # lines accepted although Whisper heard a word differently: worth one listen
CB = {"exaggeration": 0.5, "cfg_weight": 0.5, "chatterbox": "ab55923", "whisper": "small.en", "judge": "utmos22-strong",
      "tries": 8,              # takes per line before Kokoro says it (hard faults: words, clicks, stalls, noise, clipping)
      "soft_tries": 3,         # takes with the right words but below the quality bar before keeping the best of them
      "gap_max": 0.8,          # longest silence inside a sentence, seconds
      "rate": (1.6, 4.6),      # words a second for a line of four words or more
      "mos_min": 3.8,          # UTMOS of the whole take (clean Kokoro scores about 4.4; a glitch drops it by about 1)
      "mos_window_min": 3.4,   # UTMOS of the worst 2-second stretch
      "sim_min": 0.75,         # likeness to the af_heart reference (cosine of voice-encoder embeddings)
      "clarity_min": 0.35,     # Whisper's confidence in its least clear word (a blurred "it at" scores low; tune by ear)
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

_WRITTEN = [                                         # how Whisper writes things the voice says in words
    (r"(?<=[a-z])\+\+", " plus plus "), (r"\+", " plus "), (r"(?<=[a-z])#", " sharp "), (r"%", " percent "),
    (r"&", " and "), (r"<=", " less than or equal to "), (r">=", " greater than or equal to "), (r"!=", " not equal to "),
    (r"==", " equals "), (r"=", " equals "), (r"<", " less than "), (r">", " greater than "), (r"\bo\(", " o of "),
    (r"\.(?=[a-z])", " dot "),                       # onehintaway.com, "onehintaway .com"
]

def spoken_form(text):
    """Text as it is said: numbers, decimals and symbols in words, lower case."""
    t = re.sub(r"(?<=\d),(?=\d{3})", "", text.lower().replace("’", "'"))
    for pat, rep in _WRITTEN:
        t = re.sub(pat, rep, t)
    t = re.sub(r"(\d+)\.(\d+)", lambda m: f" {_num(int(m.group(1)))} point " + " ".join(_ONES[int(d)] for d in m.group(2)) + " ", t)
    t = re.sub(r"\d+", lambda m: " " + _num(int(m.group())) + " ", t)
    return re.sub(r"\b(hundred|thousand) and\b", r"\1", t)

def norm_words(text):
    """Words to compare what was meant with what Whisper heard: lower case, numbers and symbols as words, no punctuation.
    Every word counts (an extra "and" is an extra word); only the "and" inside a number ("a hundred and two") is dropped."""
    return re.findall(r"[a-z]+", spoken_form(text).replace("'", ""))

def written(token):
    """Whisper wrote this word with digits or symbols: a formatting choice, not something the voice did."""
    return bool(re.search(r"[0-9+#%&=<>^/*()\[\]@$]|[a-z]\.[a-z]|^\.", token.lower()))

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

def sound_alike(exp, heard, flags=None):
    """Whisper wrote the right sounds in other words ("Two Sum" as "twosome", "seen" as "scene")?
    A differing stretch of plain words must sound the same, give or take one sound in five, and an extra or missing
    plain word never passes. A stretch Whisper wrote with digits or symbols ("C++", ".com", "O(n)") is its formatting:
    it passes within two sounds in five. Returns (True, "how Whisper spelled it") or (False, "")."""
    from difflib import SequenceMatcher
    flags = flags or [False] * len(heard); notes = []
    for op, i0, i1, j0, j1 in SequenceMatcher(None, exp, heard, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        fmt = any(flags[j0:j1]) or (j0 == j1 and any(flags[max(0, j0 - 1): j0 + 1]))
        if (i0 == i1 or j0 == j1) and not fmt:
            return False, ""
        a, b = _phones(exp[i0:i1]), _phones(heard[j0:j1])
        if _edits(a, b) > max(1, int((0.4 if fmt else 0.2) * max(len(a), len(b)))):
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

class VoiceDown(Exception):
    """The Chatterbox helper could not start or stopped: lines fall back to Kokoro instead of stopping the render."""

_cb_restarts = 0

def _cb_ask(req):
    global _cb, _cb_restarts
    if _cb == "down":
        raise VoiceDown("the Chatterbox helper is not running")
    try:
        if _cb is None:
            py = os.environ.get("CB_PYTHON")
            if not py:
                raise VoiceDown("CB_PYTHON is not set (the videos workflow sets up the Chatterbox environment)")
            _cb = subprocess.Popen([py, "-u", str(ROOT / "cb_worker.py")], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
                                   env={**os.environ, "CB_WHISPER": CB["whisper"]})
            if not json.loads(_cb.stdout.readline() or "{}").get("ready"):
                raise VoiceDown("the Chatterbox helper did not start (see the log above)")
        _cb.stdin.write(json.dumps(req) + "\n"); _cb.stdin.flush()
        line = _cb.stdout.readline()
        if not line:
            raise VoiceDown("the Chatterbox helper stopped (see the log above)")
        return json.loads(line)
    except (VoiceDown, OSError, ValueError) as e:
        if isinstance(_cb, subprocess.Popen):
            _cb.kill()
        _cb_restarts += 1
        _cb = None if _cb_restarts <= 1 else "down"          # one restart, then Kokoro for the rest of the video
        raise VoiceDown(str(e))

def _cb_junk(a, sr, words):
    """Sound well after the last word or well before the first (a breath is fine, a mumble is not)."""
    if not words:
        return True
    hop = int(0.02 * sr); n = len(a) // hop
    loud = np.sqrt(np.mean(a[: n * hop].reshape(n, hop) ** 2, axis=1)) > 0.02 * max(1e-6, np.abs(a).max()) * 2
    head = loud[: max(0, int((words[0][1] - 0.35) / 0.02))].sum() * 0.02
    tail = loud[int((words[-1][2] + 0.35) / 0.02):].sum() * 0.02
    return head > 0.4 or tail > 0.4

# Breathing room, measured as real silence (voice off to voice on). Kokoro's post 05 measures 0.46 s after a statement,
# 0.62 s after a question and 0.55 s between lines; these are a little longer, because Chatterbox speaks with more energy.
PAUSE = {".": 0.5, "?": 0.65, "!": 0.55}
LINE_TAIL = 0.28          # silence after a line; with the scene's 0.22 s gap that is about 0.55 s between lines

def _gap_after(sentence):
    """Silence after a sentence: a question gets the longest, a statement the shortest."""
    p = sentence.rstrip()[-1:] if sentence.strip() else "."
    return PAUSE.get(p, PAUSE["."])

# ---- Shaping a Chatterbox take: silence is the only thing ever changed (root-cause fix, 28 November 2026).
# Jaga heard "lines", "index", "needs", "times" lose their last sound, and "Re…member", "Firs…t" split by a pause.
# Both came from the shaping, not from Chatterbox: sentence ends were found as "louder than 12% of the peak" plus 80 ms,
# which cuts every quiet ending (s, z, ks, st), and sentences were cut at "the quietest 10 ms near Whisper's word time",
# which lands inside a word whenever Whisper's time is off (the silent stop before the t of "first"). And the checks
# judged the raw take, never the shaped audio that ships. Now:
#   1. Voice is measured, not guessed: a 10 ms frame is voice if it stands out from this take's own noise floor in the
#      whole band or above 3.5 kHz (where s, z, f, th and the burst of t live), down to 45 dB below the speech.
#   2. Only silence is cut, lengthened or faded. A sentence pause goes into a real silence of at least 0.12 s (longer
#      than the silent stop inside "first"), the longest one between the two sentences' edge words. If a take has no
#      such silence there, nothing is inserted and the take counts as "sentences run together" (another take is tried).
#   3. A sound is removed only if it cannot belong to a word: under 80 ms with 0.15 s of silence on both sides, or a
#      quiet breath at a sentence's edge set 0.15 s apart from its words.
#   4. Every shaped line is compared with its take: each kept stretch of voice must be there sample for sample.
#      If not, the line is used unshaped (and noted), so a shaping mistake can never cut a word.
#   5. Raw takes are cached, not shaped ones: changing the shaping or the checks never needs the voice made again.
VAD = {"hop": 0.01,          # frame, seconds
       "below_speech": 45.0,  # voice reaches down to this many dB below the take's speech level (its 95th percentile)
       "above_floor": 10.0,  # ... and must stand this far above its noise floor (10th percentile)
       "hf_hz": 3500,        # the band where quiet consonants live
       "pause_min": 0.12,    # a silence that can hold a sentence pause; shorter ones can be a stop inside a word
       "apart": 0.15,        # a sound this far from every other sound is not part of a word
       "blip_max": 0.08,     # an isolated sound this short is a click or a fragment: removed
       "weak": 18.0,         # an edge sound this far below speech (whole band and high band) is a breath: removed
       "click_max": 0.06,    # a sound this short, set apart by click_gap on both sides, after a word that does not end
       "click_gap": 0.03,    #   in a stop (p t k b d g), is a click Chatterbox added ("letter, [tick] add one")
       "click_voicing": 10.0,  # ... if it has no voice in it: its whole band is within this many dB of its high band
                             #   (a short word like "a" or "the" is voiced and is never a click)
       "stall": 0.2}         # silence this long inside one word is a stall ("Rem … ember")
_HP = None
_STOPS = set("pbtdkɡgʔ")

def _to48(a, sr):
    a = np.asarray(a, np.float64)
    return (resample_poly(a, SR, sr) if sr != SR else a).astype(np.float32)

def _vad(a, thr=None):
    """Voice per 10 ms frame of a 48 kHz take: (mask, thresholds, whole-band dB, high-band dB, speech levels)."""
    global _HP
    from scipy.signal import butter, sosfiltfilt
    if _HP is None:
        _HP = butter(4, VAD["hf_hz"], "hp", fs=SR, output="sos")
    hop = int(VAD["hop"] * SR); n = len(a) // hop
    if n < 2:
        return np.zeros(n, bool), thr or (0.0, 0.0), np.zeros(n), np.zeros(n), (0.0, 0.0)
    x = np.asarray(a[: n * hop], np.float64)
    full = 10 * np.log10((x.reshape(n, hop) ** 2).mean(axis=1) + 1e-10)
    high = 10 * np.log10((sosfiltfilt(_HP, x).reshape(n, hop) ** 2).mean(axis=1) + 1e-10)
    ref = (float(np.percentile(full, 95)), float(np.percentile(high, 95)))
    if thr is None:
        thr = tuple(max(r - VAD["below_speech"], float(np.percentile(d, 10)) + VAD["above_floor"]) for r, d in zip(ref, (full, high)))
    return (full > thr[0]) | (high > thr[1]), thr, full, high, ref

def _runs_of(mask):
    """Stretches of True as (first frame, frame after the last)."""
    m = np.concatenate([[False], np.asarray(mask, bool), [False]]).astype(np.int8)
    d = np.flatnonzero(np.diff(m))
    return [(int(s), int(e)) for s, e in zip(d[::2], d[1::2])]

def _sent_ranges(heard, counts):
    """First and last heard word of each sentence (Whisper may split or join a word: spread proportionally)."""
    scale = len(heard) / max(1, sum(counts)); rng, i = [], 0
    for c in counts:
        j0 = min(len(heard) - 1, int(round(i * scale)))
        j1 = min(len(heard) - 1, max(j0, int(round((i + c) * scale)) - 1))
        rng.append((j0, j1)); i += c
    return rng

def _ends_in_stop(word):
    p = _phones(norm_words(word)); return bool(set(p[-2:]) & _STOPS)

def _starts_with_stop(word):
    p = _phones(norm_words(word)); return bool(p[:1]) and p[0] in _STOPS

def _cb_plan(a, heard, text):
    """Read a 48 kHz take: where its voice is, which sounds are not words, where each sentence pause goes, and the
    faults only the sound shows (clicks, stalls, sentences run together). Changes nothing."""
    sents = [x for x in _SENT.split(text.strip()) if x]
    voiced, thr, full, high, ref = _vad(a)
    nf, hs = len(voiced), VAD["hop"]; fr = lambda s: int(round(s / hs))
    runs = _runs_of(voiced)
    plan = {"thr": thr, "sents": sents, "pieces": [], "dropped": [], "joined": [], "clicks": [], "stalls": [], "bounds": []}
    if not runs:
        return plan
    inf = 10 ** 9
    gap_b = lambda rs, i: rs[i][0] - rs[i - 1][1] if i else inf
    gap_a = lambda rs, i: rs[i + 1][0] - rs[i][1] if i + 1 < len(rs) else inf
    keep = []
    for i, r in enumerate(runs):                     # 3a. clicks and fragments set apart from everything
        if r[1] - r[0] <= fr(VAD["blip_max"]) and gap_b(runs, i) >= fr(VAD["apart"]) and gap_a(runs, i) >= fr(VAD["apart"]):
            plan["dropped"].append(r)
        else:
            keep.append(r)
    if not keep:
        return plan
    # 2. sentence pauses: the longest real silence (>= pause_min) between a sentence's last word and the next one's first
    counts = [len(norm_words(x)) for x in sents]
    rng = _sent_ranges(heard, counts) if heard else []
    gaps = [(keep[i][1], keep[i + 1][0]) for i in range(len(keep) - 1)]
    weak = lambda r: full[r[0]:r[1]].max() < ref[0] - VAD["weak"] and high[r[0]:r[1]].max() < ref[1] - VAD["weak"]
    words_in = lambda f0, f1: sum(min(e, f1) - max(s, f0) for s, e in keep if s < f1 and e > f0 and not weak((s, e)))
    chosen, last = [], 0
    for k in range(len(sents) - 1):
        b = None
        if rng:
            lo, hi = heard[rng[k][1]][1] - 0.1, heard[rng[k + 1][0]][2] + 0.15
            after = fr(heard[rng[k + 1][1]][2] + 0.3)     # a sentence (even "Yes.") must have words on both sides
            cands = [g for g in gaps if g[1] - g[0] >= fr(VAD["pause_min"]) and g[0] * hs < hi and g[1] * hs > lo and g[0] >= last
                     and words_in(last, g[0]) >= fr(0.12) and words_in(g[1], max(after, g[1] + 1)) >= fr(0.12)]
            if cands:
                mid = (lo + hi) / 2
                b = max(cands, key=lambda g: (g[1] - g[0], -abs((g[0] + g[1]) / 2 * hs - mid)))
                last = b[1]
        plan["bounds"].append(b)
        if b is None:
            plan["joined"].append(k)
        else:
            chosen.append((b, k))
    # pieces: runs between chosen pauses, each with the sentences it holds
    starts = {b[1]: k for b, k in chosen}; pieces, cur, first = [], [], 0
    for r in keep:
        if r[0] in starts and cur:
            pieces.append({"runs": cur, "sents": (first, starts[r[0]])}); first = starts[r[0]] + 1; cur = []
        cur.append(r)
    pieces.append({"runs": cur, "sents": (first, len(sents) - 1)})
    for p in pieces:                                 # 3b. a quiet breath at a sentence's edge, set apart from its words
        rs = p["runs"]
        while len(rs) > 1 and rs[1][0] - rs[0][1] >= fr(VAD["apart"]) and weak(rs[0]):
            plan["dropped"].append(rs.pop(0))
        while len(rs) > 1 and rs[-1][0] - rs[-2][1] >= fr(VAD["apart"]) and weak(rs[-1]):
            plan["dropped"].append(rs.pop())
    plan["pieces"] = pieces
    # faults only the sound shows (the take is judged; nothing is removed for these)
    allk = [r for p in pieces for r in p["runs"]]
    starts_w = [h[1] for h in heard]
    for i, r in enumerate(allk):
        unvoiced = float(np.max(full[r[0]:r[1]] - high[r[0]:r[1]])) < VAD["click_voicing"]
        if (r[1] - r[0] <= fr(VAD["click_max"]) and unvoiced and gap_b(allk, i) >= fr(VAD["click_gap"])
                and gap_a(allk, i) >= fr(VAD["click_gap"])):
            t = r[0] * hs
            prev = next((h[0] for h, s in zip(reversed(heard), reversed(starts_w)) if s <= t), None)
            nxt = next((h[0] for h, s in zip(heard, starts_w) if s > t), None)
            if prev is not None and not _ends_in_stop(prev) and not (nxt is not None and _starts_with_stop(nxt)):
                plan["clicks"].append((round(t, 2), prev, nxt))
    for g0, g1 in zip([r[1] for r in allk], [r[0] for r in allk[1:]]):
        if (g1 - g0) * hs >= VAD["stall"]:
            for w, s, e, *_ in heard:
                if s + 0.08 <= g0 * hs and g1 * hs <= e - 0.08:
                    plan["stalls"].append((round(g0 * hs, 2), w)); break
    return plan

def _even_spans(t0, t1, sents):
    """Sentence times spread by word count, for a line that could not be shaped."""
    w = np.cumsum([0] + [max(1, len(norm_words(x))) for x in sents or ["."]]) / max(1, sum(max(1, len(norm_words(x))) for x in sents or ["."]))
    return [(round(t0 + (t1 - t0) * x, 3), round(t0 + (t1 - t0) * y, 3)) for x, y in zip(w, w[1:])]

def _edge_fades(seg, lead, tail):
    """Fade in over the first `lead` samples and out over the last `tail`: the take's own silence around a sentence."""
    if lead > 0:
        seg[:lead] *= np.linspace(0, 1, lead, dtype=np.float32)
    if tail > 0:
        seg[-tail:] *= np.linspace(1, 0, tail, dtype=np.float32)

def _cb_assemble(a, sr, heard, text, level=True):
    """The finished line from a raw take: sentences with the take's own voice untouched, exact pauses between them
    (0.5 s after a statement, 0.65 after a question, 0.55 after '!', or the take's own if longer, up to 0.25 s more),
    20 ms of the take's silence faded at each edge, LINE_TAIL at the end, levelled.
    Returns (audio at 48 kHz, [(start, end) per sentence], info)."""
    a = _to48(a, sr)
    plan = _cb_plan(a, heard, text)
    sents, hop = plan["sents"], int(VAD["hop"] * SR)
    info = {"joined": plan["joined"], "dropped": round(sum(e - s for s, e in plan["dropped"]) * VAD["hop"], 2)}
    if not plan["pieces"]:
        return _level(a), _even_spans(0.0, len(a) / SR, sents), {**info, "unshaped": "no voice found"}
    pad = int(0.02 * SR); out = [np.zeros(pad, np.float32)]; t = pad / SR; spans, cores = [], []
    pieces = plan["pieces"]
    for p, pc in enumerate(pieces):
        s0, s1 = pc["runs"][0][0] * hop, pc["runs"][-1][1] * hop
        x0, x1 = max(0, s0 - pad), min(len(a), s1 + pad)
        seg = a[x0:x1].copy()
        for d0, d1 in plan["dropped"]:                 # a removed fragment inside a sentence becomes silence
            if s0 <= d0 * hop < s1:
                seg[d0 * hop - x0: d1 * hop - x0] = 0.0
        _edge_fades(seg, s0 - x0, x1 - s1)
        base = t - x0 / SR                               # take time -> line time for this piece
        k0, k1 = pc["sents"]
        if k1 > k0 and heard:                            # sentences that stayed together: split at Whisper's estimate
            rng = _sent_ranges(heard, [len(norm_words(x)) for x in sents]); edges = [s0 / SR]
            for k in range(k0, k1):
                edges.append(min(max((heard[rng[k][1]][2] + heard[rng[k + 1][0]][1]) / 2, edges[-1]), s1 / SR))
            edges.append(s1 / SR)
            spans += [(round(base + e0, 3), round(base + e1, 3)) for e0, e1 in zip(edges, edges[1:])]
        else:
            spans += [(round(base + s0 / SR, 3), round(base + s1 / SR, 3))] * (k1 - k0 + 1)
        cores.append((len(out), s0 - x0, s0, s1, [(d0 * hop, d1 * hop) for d0, d1 in plan["dropped"] if s0 <= d0 * hop < s1]))
        out.append(seg); t += len(seg) / SR
        if p + 1 < len(pieces):
            natural = (pieces[p + 1]["runs"][0][0] * hop - s1) / SR
            want = _gap_after(sents[k1])
            gap = min(max(natural, want), want + 0.25) - (x1 - s1) / SR - min(pad, pieces[p + 1]["runs"][0][0] * hop) / SR
            out.append(np.zeros(int(max(0.0, gap) * SR), np.float32)); t += max(0.0, gap)
    out.append(np.zeros(int(LINE_TAIL * SR), np.float32))
    # 4. the proof: every kept stretch of voice is in the line, sample for sample
    for i, off, s0, s1, holes in cores:
        want = a[s0:s1].copy()
        for h0, h1 in holes:
            want[h0 - s0: h1 - s0] = 0.0
        if not np.array_equal(out[i][off: off + (s1 - s0)], want):
            v = np.flatnonzero(_vad(a)[0]); lo, hi = v[0] * hop, (v[-1] + 1) * hop
            plain = np.concatenate([np.zeros(pad, np.float32), a[max(0, lo - pad): hi + pad], np.zeros(int(LINE_TAIL * SR), np.float32)])
            return _level(plain), _even_spans(pad / SR, (pad + hi - lo) / SR, sents), {**info, "unshaped": "shaping check failed"}
    a = np.concatenate(out)
    return (_level(a) if level else a), spans, info

def _cb_gates(t, exp, sents_end):
    """Judge one take. Hard faults are never shipped; soft faults send it back for another take."""
    hard, soft, words = [], [], t["words"]
    hw = [h[0] for h in t["heard"]]
    if hw != exp:
        same, how = sound_alike(exp, hw, [h[3] for h in t["heard"]] if t["heard"] and len(t["heard"][0]) > 3 else None)
        if same:
            t["spelled"] = how                     # the voice said the words; Whisper spelled them its own way
        else:
            hard.append("words differ")
    if t["junk"]:
        hard.append("sound before or after the words")
    if t["peak"] >= 0.999:
        hard.append("clipped")
    for (w0, _, e0, *_), (_, s1, *_) in zip(words, words[1:]):
        if s1 - e0 > CB["gap_max"] and not w0.rstrip().endswith(sents_end):
            hard.append(f"{s1 - e0:.1f} s silence after {w0.strip()!r}"); break
    plan = t.get("plan") or {}
    if plan.get("clicks"):                         # 28 Nov 2026: a tick between "letter," and "add one"
        hard.append("a click after " + ", ".join(repr(c[1]) for c in plan["clicks"][:2]))
    if plan.get("stalls"):                         # a word stopped and restarted ("Rem … ember")
        hard.append("a stall inside " + ", ".join(repr(s[1]) for s in plan["stalls"][:2]))
    span = (words[-1][2] - words[0][1]) if words else 0.0     # first word to last, natural pauses included
    rate = len(exp) / max(span, 0.3)
    t["rate"] = round(rate, 2)
    if len(exp) >= 4 and not CB["rate"][0] <= rate <= CB["rate"][1]:
        soft.append(f"{rate:.1f} words a second")
    if plan.get("joined"):                         # no real silence to hold a sentence pause: another take may pause
        soft.append("sentences run together after " + ", ".join(repr(plan["sents"][k][-24:]) for k in plan["joined"][:2]))
    clear = t.get("clarity", 1.0)
    if clear < CB["clarity_min"]:                  # 28 Nov 2026: "start it at one" came out blurred
        soft.append(f"an unclear word ({t.get('unclear', '?')!r}, {clear:.2f})")
    if t["mos"] < CB["mos_min"]:
        soft.append(f"naturalness {t['mos']:.2f}")
    if t["mos_min"] < CB["mos_window_min"]:
        soft.append(f"a rough stretch ({t['mos_min']:.2f})")
    if t["vsim"] < CB["sim_min"]:
        soft.append(f"voice likeness {t['vsim']:.2f}")
    return hard, soft

def _fallback(text, why):
    """Kokoro's af_heart says the line (always the right words), levelled like the rest. Listed in the listen list."""
    global LAST_META
    a, spans = _kokoro_human(text)
    a = _level(a)
    meta = {"spans": [list(x) for x in spans], "fallback": "kokoro", "note": f"said by Kokoro: {why}", "takes": CB["tries"]}
    LAST_META = {**meta, "text": spoken_text(text)}
    VOICE_NOTES.append(f"{spoken_text(text)!r}: said by Kokoro ({why})")
    print(f"   kokoro fallback for {spoken_text(text)[:50]!r}: {why}", flush=True)
    return a, spans

def _hotwords(text):
    """Names and terms Whisper should spell the script's way (Two Sum, LeetCode, anagram): capitalised words
    inside a sentence and long words. Only spelling hints: the sound still decides what Whisper hears."""
    out = []
    for sent in _SENT.split(spoken_text(text)):
        ws = re.findall(r"[A-Za-z][A-Za-z']*", sent)
        out += [w for k, w in enumerate(ws) if (k and w[0].isupper()) or len(w) >= 9]
    return " ".join(dict.fromkeys(out))

def _level(a):
    """The same speech loudness for every line, whichever voice said it."""
    hop = int(0.02 * SR); n = len(a) // hop
    if n:
        r = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(axis=1)); speech = r[r > 0.1 * r.max()]
        if len(speech):
            g = CB["speech_rms"] / max(1e-6, float(np.sqrt((speech ** 2).mean())))
            a = a * min(g, 0.95 / max(1e-6, float(np.abs(a).max())))
    return a.astype(np.float32)

def _cb_take(said, seed, hot):
    """One raw take and what the three listeners made of it, cached by everything that shapes them. Shaping and the
    checks run fresh on every use, so changing either never needs the voice made again."""
    gen = {k: CB[k] for k in ("exaggeration", "cfg_weight", "chatterbox", "whisper", "judge")}
    key = hashlib.sha1(f"cbtake|{said}|{seed}|{hot}|{sorted(gen.items())}|t1".encode()).hexdigest()[:16]
    fa, fj = CACHE / f"cbt-{key}.wav", CACHE / f"cbt-{key}.json"
    if fa.exists() and fj.exists():
        a, sr = sf.read(fa, dtype="float32")
        return a, sr, json.loads(fj.read_text())
    tmp = CACHE / f"cbt-{key}-new.wav"
    ans = _cb_ask({"text": said, "seed": seed, "out": str(tmp), "ref": str(_cb_ref()),
                   "exaggeration": CB["exaggeration"], "cfg_weight": CB["cfg_weight"], "hotwords": hot})
    if "error" in ans:
        return None, 0, ans
    a, sr = sf.read(tmp, dtype="float32"); tmp.unlink(missing_ok=True)
    if a.ndim > 1:
        a = a.mean(axis=1)
    sf.write(fa, a, sr); fj.write_text(json.dumps(ans))
    return a, sr, ans

def _cb_human(text):
    """One line from Chatterbox, judged by its checks (words, clicks and stalls, timing, clarity, naturalness, likeness
    to af_heart), shaped by changing silence only. Returns (audio, sentence spans). LAST_META describes the take for
    the video's listen list."""
    global LAST_META
    from difflib import SequenceMatcher
    said = _cb_text(text); exp = norm_words(spoken_text(text)); spoken = spoken_text(text); hot = _hotwords(text)
    takes, pick, note = [], None, ""
    for seed in range(1, CB["tries"] + 1):
        try:
            a, sr, ans = _cb_take(said, seed, hot)
        except VoiceDown as e:
            return _fallback(text, f"Chatterbox unavailable: {e}")
        if a is None:
            print(f"   chatterbox take {seed} failed: {ans['error']}", flush=True); continue
        heard = []
        for w in ans["words"]:
            heard += [(x, w[1], w[2], written(w[0])) for x in norm_words(w[0])]
        hw = [h[0] for h in heard]
        hotset = set(norm_words(hot))                 # a name Whisper was told to expect, or digits, is spelling doubt, not sound
        probs = [(w[3], w[0].strip()) for w in ans["words"]
                 if len(w) > 3 and norm_words(w[0]) and not written(w[0]) and not set(norm_words(w[0])) & hotset]
        clear = min(probs) if probs else (1.0, "")
        t = {"seed": seed, "a": a, "sr": sr, "heard": heard, "words": ans["words"], "junk": _cb_junk(a, sr, ans["words"]),
             "peak": float(np.abs(a).max()) if len(a) else 0.0, "mos": ans.get("mos", 5.0), "mos_min": ans.get("mos_min", 5.0),
             "vsim": ans.get("sim", 1.0), "match": SequenceMatcher(None, exp, hw).ratio(), "clarity": clear[0], "unclear": clear[1],
             "plan": _cb_plan(_to48(a, sr), heard, spoken), "text": " ".join(w[0] for w in ans["words"])}
        t["hard"], t["soft"] = _cb_gates(t, exp, (".", "?", "!", ":", ";"))
        takes.append(t)
        print(f"   take {seed}: " + ("ok" if not t["hard"] + t["soft"] else "; ".join(t["hard"] + t["soft"]))
              + f" | mos {t['mos']:.2f}/{t['mos_min']:.2f} likeness {t['vsim']:.2f}", flush=True)
        if not t["hard"] and not t["soft"]:
            pick = t; break
        sound = [x for x in takes if not x["hard"]]
        if len(sound) >= CB["soft_tries"]:            # the words are right but it is below the bar every time: keep the best
            pick = min(sound, key=lambda x: (len(x["soft"]), -x["clarity"], -x["mos_min"], -x["mos"], -x["vsim"]))
            note = "below the quality bar: " + "; ".join(pick["soft"]); break
    if pick is None:                              # never ship a doubtful take and never stop the render: Kokoro says it
        best = max(takes, key=lambda x: (len(x["hard"]) == 1, x["match"], x["mos_min"])) if takes else None
        why = f"no clean Chatterbox take in {len(takes)}" + (f" (closest: {'; '.join(best['hard'])}; heard {best['text']!r})" if best else "")
        return _fallback(text, why)
    a, spans, info = _cb_assemble(pick["a"], pick["sr"], pick["heard"], spoken)
    if info.get("unshaped"):
        note = (note + "; " if note else "") + f"used unshaped ({info['unshaped']})"
    meta = {"spans": spans, "seed": pick["seed"], "takes": len(takes), "heard": pick["text"], "note": note,
            "mos": pick["mos"], "mos_min": pick["mos_min"], "likeness": pick["vsim"], "rate": pick.get("rate"),
            "clarity": round(pick["clarity"], 2), "spelled": pick.get("spelled", "")}
    LAST_META = {**meta, "text": spoken}
    if note:
        VOICE_NOTES.append(f"{spoken!r}: {note}")
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
