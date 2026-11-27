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
        for at, k in self.fx:
            s = sfx(k); i = int(at * SR)
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
