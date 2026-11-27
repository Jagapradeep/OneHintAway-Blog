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
    heard = [(x, s, e) for w, s, e in words for x in E.norm_words(w)]
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
