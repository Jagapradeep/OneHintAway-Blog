"""Regression tests for the Chatterbox checks: every voice problem found by ear becomes a test here, so it cannot
come back. No models needed (synthetic audio and word timings). Run: python youtube/engine/test_voice.py"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import engine as E

SR = 24000

def take(words, text, mos=4.3, mos_min=4.1, sim=0.88, length=None, peak=0.5):
    """A fake take: a tone during each word, silence between, Whisper's words as given."""
    n = int((length or words[-1][2] + 0.4) * SR); a = np.zeros(n, np.float32)
    for _, s, e in words:
        k = np.arange(int(s * SR), int(e * SR)); a[k] = peak * np.sin(2 * np.pi * 220 * k / SR)
    heard = [(x, s, e, E.written(w)) for w, s, e in words for x in E.norm_words(w)]
    t = {"a": a, "sr": SR, "heard": heard, "words": words, "junk": E._cb_junk(a, SR, words), "peak": float(np.abs(a).max()),
         "mos": mos, "mos_min": mos_min, "vsim": sim}
    return t, E.norm_words(E.spoken_text(text))

def gates(words, text, **kw):
    t, exp = take(words, text, **kw)
    return E._cb_gates(t, exp, (".", "?", "!", ":", ";"))

def spread(text, start=0.1, step=0.32):
    ws = text.split()
    return [[w, round(start + i * step, 3), round(start + i * step + step - 0.05, 3)] for i, w in enumerate(ws)]

def test_extra_and_is_caught():          # 27 Nov 2026: "And thanks for watching." passed as "Thanks for watching."
    hard, _ = gates(spread("And thanks for watching."), "Thanks for watching.")
    assert "words differ" in hard, hard
    assert E.norm_words("a hundred and two") == E.norm_words("a hundred two")   # the "and" inside a number is fine

def test_sound_alike_spelling_passes():   # 28 Nov 2026: "Two Sum" heard as "twosome" failed a Short 8 times
    for said, heard in [("This Two Sum looks right.", "This twosome looks right."),
                        ("the code is on one hint away dot com", "The code is on onehintaway.com"),
                        ("everything you have seen", "everything you have scene")]:
        hard, _ = gates(spread(heard), said)
        assert not hard, (said, heard, hard)

def test_whisper_formatting_passes():     # 28 Nov 2026: "onehintaway .com" and "C++" failed correct takes 8 times
    for said, heard in [("Every line is on one hint away dot com.", "Every line is on onehintaway .com"),
                        ("Every line is on one hint away dot com.", "Every line is on onehintaway.com."),
                        ("In C plus plus, a missing key already starts at zero.", "In C++, a missing key already starts at zero."),
                        ("In C sharp it is the same.", "In C# it is the same."),
                        ("This runs in O of n time.", "This runs in O(n) time."),
                        ("Half is zero point five.", "Half is 0.5."),
                        ("That is fifty percent of the pairs.", "That is 50% of the pairs."),
                        ("Check i plus plus here.", "Check i++ here."),
                        ("LeetCode two hundred forty two.", "LeetCode 242."),
                        ("When x equals three, stop.", "When x = 3, stop.")]:
        hard, _ = gates(spread(heard), said)
        assert not hard, (said, heard, hard)

def test_real_garbles_still_fail():       # the rough "Is" takes from the 27 Nov voice test, and the extra "and"
    for said, heard in [("Is four on the list?", "It was four on the list."), ("Is four on the list?", "This 4 on the list."),
                        ("Is four on the list?", "Yeah, is 4 on the list?"), ("Is four on the list?", "One is four on the list."),
                        ("In banana, n comes twice.", "In banana, and comes twice."),
                        ("Which two add up to ten?", "Which two add up to 10? 10.")]:
        hard, _ = gates(spread(heard), said)
        assert "words differ" in hard, (said, heard, hard)

def test_numbers_match_words():
    assert E.norm_words("Is 4 on the list? 10, 1,000") == E.norm_words("Is four on the list? ten, one thousand")

def test_clean_take_passes():
    hard, soft = gates(spread("Five numbers. Which two add up to ten?"), "Five numbers. Which two add up to ten?")
    assert not hard and not soft, (hard, soft)

def test_long_gap_inside_a_sentence():
    w = spread("Which two add up to ten?"); w[3:] = [[x, s + 1.2, e + 1.2] for x, s, e in w[3:]]
    hard, _ = gates(w, "Which two add up to ten?")
    assert any("silence" in h for h in hard), hard

def test_mumble_after_the_line():
    t, exp = take(spread("Is four on the list?"), "Is four on the list?", length=4.0)
    k = np.arange(int(2.6 * SR), int(3.6 * SR)); t["a"][k] = 0.4 * np.sin(2 * np.pi * 180 * k / SR)
    t["junk"] = E._cb_junk(t["a"], SR, t["words"])
    assert "sound before or after the words" in E._cb_gates(t, exp, (".", "?", "!"))[0]

def test_clipping():
    hard, _ = gates(spread("Remember the map."), "Remember the map.", peak=1.0)
    assert "clipped" in hard, hard

def test_rough_and_unlike_takes_go_back():
    _, soft = gates(spread("Remember: ask the map first."), "Remember: ask the map first.", mos=3.3, mos_min=2.9, sim=0.6)
    assert any("naturalness" in s for s in soft) and any("rough" in s for s in soft) and any("likeness" in s for s in soft), soft

def test_rushed_line():
    _, soft = gates(spread("Then three asks for its partner, which is three.", step=0.12), "Then three asks for its partner, which is three.")
    assert any("words a second" in s for s in soft), soft

def test_pause_after_a_question():         # 27 Nov 2026: "is four here?" ran straight into the next sentence
    text = "Now six arrives and asks: is four here? You don't search the room. Wrong!"
    w = spread(text, step=0.3)
    t, exp = take(w, text)
    a, spans = E._cb_shape(t["a"], SR, t["heard"], text, len(exp))
    gaps = [round(b[0] - x[1], 2) for x, b in zip(spans, spans[1:])]
    assert gaps[0] >= 0.5 - 0.02 and gaps[1] >= 0.34 - 0.02, gaps

def test_lines_are_levelled():
    t1, e1 = take(spread("Is four on the list?"), "Is four on the list?", peak=0.2)
    t2, e2 = take(spread("Is four on the list?"), "Is four on the list?", peak=0.6)
    a1, _ = E._cb_shape(t1["a"], SR, t1["heard"], "Is four on the list?", len(e1))
    a2, _ = E._cb_shape(t2["a"], SR, t2["heard"], "Is four on the list?", len(e2))
    r = lambda a: float(np.sqrt((a[np.abs(a) > 0.01] ** 2).mean()))
    assert abs(20 * np.log10(r(a1) / r(a2))) < 1.0

def test_letters_are_quoted_for_chatterbox():
    assert E._cb_text("In banana, [a](/ˈeɪ/) comes three times, *twice* for [n](/ˈɛn/).") == 'In banana, "a" comes three times, twice for "n".'

def test_lone_scene_note_is_dropped():   # 27/28 Nov 2026: a "click" before "Thanks for watching." was the scene-change note
    import tempfile
    v = E.Video("t", 320, 180)
    v.t = 6.0; v.fx = [(1.0, "turn"), (4.0, "turn")]
    tone = (0.3 * np.sin(2 * np.pi * 200 * np.arange(int(0.8 * E.SR)) / E.SR)).astype(np.float32)
    v.clips = [(1.35, tone)]                                   # the voice follows the first note only
    with tempfile.TemporaryDirectory() as d:
        v.mix(Path(d) / "m.wav")
    assert v.fx_dropped == [4.0], v.fx_dropped

def test_outro_has_no_scene_note():      # the ending stays quiet: no note right before "Thanks for watching."
    import yt
    spec = {"number": 0, "slug": "t", "long": {"scenes": [{"id": "a", "layout": "big", "items": [{"text": "Hi"}], "say": ["Hello there."]}]},
            "_channel": {"outro": {"long": True, "text": "Thanks for watching.", "say": "Thanks for watching."}}}
    vid, _ = yt.build(spec, "long", "af_heart")
    turns = [t for t, k in vid.fx if k == "turn"]
    assert len(turns) == len([x for x in vid.scenes if x["id"] != "outro"]), (turns, [x["id"] for x in vid.scenes])

def _runs(b, thr=0.05):
    h = int(0.01 * E.SR); n = len(b) // h; r = np.sqrt((b[: n * h].reshape(n, h) ** 2).mean(axis=1)); L = r > thr; out, i = [], 0
    while i < n:
        if L[i]:
            j = i
            while j < n and L[j]:
                j += 1
            out.append((i * 0.01, j * 0.01)); i = j
        else:
            i += 1
    return out

def _line(rng=np.random.default_rng(0)):
    sr = E.SR; tone = lambda d, f=200, amp=0.3: (amp * np.sin(2 * np.pi * f * np.arange(int(d * sr)) / sr)).astype(np.float32)
    z = lambda d: np.zeros(int(d * sr), np.float32)
    breath = (0.03 * rng.standard_normal(int(0.1 * sr))).astype(np.float32); dip = np.full(int(0.03 * sr), 0.01, np.float32)
    a = np.concatenate([z(0.5), breath, z(0.1), tone(1.0), z(0.05), breath, z(0.3), tone(0.02, 3000, 0.4), z(0.3), tone(0.8), dip, tone(0.6), z(0.4), breath])
    return a, [(0.7, 1.7), (2.67, 3.47), (3.5, 4.1)], ["One look.", "Is four here?", "Yes."]

def test_breathing_room_between_sentences():   # 28 Nov 2026: code explanations felt rushed, sentences ran together
    a, sp, sents = _line()
    b, spans = E._breathe(a, sp, sents)
    runs = _runs(b); gaps = [round(y[0] - x[1], 2) for x, y in zip(runs, runs[1:])]
    assert len(runs) == 3, runs
    assert gaps[0] >= E.PAUSE["."] - 0.03 and gaps[1] >= E.PAUSE["?"] - 0.03, gaps
    assert abs((len(b) / E.SR - runs[-1][1]) - E.LINE_TAIL - 0.08) < 0.06, len(b) / E.SR - runs[-1][1]

def test_no_stray_sounds_or_repeats():        # 28 Nov 2026: bits of breath and noise around "Have I seen it…?"
    a, sp, sents = _line()
    b, spans = E._breathe(a, sp, sents)
    runs = _runs(b)
    assert all(y - x >= 0.3 for x, y in runs), runs                   # no click, breath or fragment survives
    assert abs(sum(y - x for x, y in runs) - 2.4) < 0.05, runs          # every sentence once: nothing cut, nothing doubled

def test_captions_follow_the_voice():         # spans are exact, not Whisper's estimate
    a, sp, sents = _line()
    b, spans = E._breathe(a, sp, sents)
    for (x, y), (s0, s1) in zip(_runs(b), spans):
        assert abs(x - s0) <= 0.02 and abs(y - s1) <= 0.02, (x, y, s0, s1)

def test_your_turn_heading_waits_for_its_section():   # 28 Nov 2026: "Your turn" showed during "Solved in this video"
    import yt
    sc = {"id": "end", "layout": "end", "title": "Your turn",
          "covered": [{"id": 1, "title": "Two Sum", "level": "Easy", "at": 0}],
          "practice": [{"id": 242, "title": "Valid Anagram", "level": "Easy", "at": 1}],
          "say": ["In this video, we solved Two Sum.", "Now it's your turn: Valid Anagram."]}
    inner = yt.lay_end(sc, yt.FMT["long"], "long")
    assert not yt.heading_errors(sc, inner, "end"), yt.heading_errors(sc, inner, "end")
    early = inner.replace('class="mono-label section" data-at="L1"', 'class="mono-label section"')
    assert yt.heading_errors(sc, early, "end"), "a heading shown early must be caught"
    assert "Your turn" not in inner.split("SOLVED")[0], "the big title must not announce Your turn up front"

def test_failed_line_falls_back_to_kokoro():   # a line that never comes out clean must not stop the render
    import tempfile
    calls = {"n": 0}
    def garble(req):
        calls["n"] += 1
        a = (0.3 * np.sin(2 * np.pi * 200 * np.arange(int(1.2 * 24000)) / 24000)).astype(np.float32)
        import soundfile as sf; sf.write(req["out"], a, 24000)
        return {"sr": 24000, "words": [["Banana", 0.1, 0.5], [f"x{calls['n']}", 0.6, 1.0]], "mos": 4.3, "mos_min": 4.2, "sim": 0.9}
    old_ask, old_cache, old_engine = E._cb_ask, E.CACHE, E.VOICE_ENGINE
    with tempfile.TemporaryDirectory() as d:
        try:
            E._cb_ask, E.CACHE = garble, Path(d); E.set_voice_engine("chatterbox"); E.VOICE_ERRORS.clear(); E.VOICE_NOTES.clear()
            ref = Path(d) / "cb-reference-af_heart.wav"; import soundfile as sf; sf.write(ref, np.zeros(2400, np.float32), E.SR)
            a, spans = E.human("Is four on the list?")
            assert E.LAST_META.get("fallback") == "kokoro" and len(a) > E.SR * 0.5 and not E.VOICE_ERRORS, E.LAST_META
            assert calls["n"] == E.CB["tries"], calls
        finally:
            E._cb_ask, E.CACHE = old_ask, old_cache; E.set_voice_engine(old_engine)

def test_missing_chatterbox_falls_back():
    import os, tempfile
    old_cache, old_engine, env = E.CACHE, E.VOICE_ENGINE, os.environ.pop("CB_PYTHON", None)
    with tempfile.TemporaryDirectory() as d:
        try:
            E.CACHE = Path(d); E._cb = None; E._cb_restarts = 0; E.set_voice_engine("chatterbox")
            a, _ = E.human("Remember the map.")
            assert E.LAST_META.get("fallback") == "kokoro" and len(a) > 0
        finally:
            E.CACHE = old_cache; E.set_voice_engine(old_engine); E._cb = None; E._cb_restarts = 0
            if env: os.environ["CB_PYTHON"] = env

if __name__ == "__main__":
    tests = [(k, f) for k, f in sorted(globals().items()) if k.startswith("test_")]
    bad = 0
    for k, f in tests:
        try:
            f(); print("ok  ", k)
        except AssertionError as e:
            bad += 1; print("FAIL", k, e)
    print(f"{len(tests) - bad} of {len(tests)} passed")
    sys.exit(1 if bad else 0)
