"""Regression tests for the Chatterbox checks and shaping: every voice problem found by ear becomes a test here, so it
cannot come back. Synthetic audio, plus Kokoro's af_heart as a real voice (its model files are set up before the tests).
Run: python youtube/engine/test_voice.py"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import engine as E

SR = 24000

def take(words, text, mos=4.3, mos_min=4.1, sim=0.88, length=None, peak=0.5, clarity=0.95):
    """A fake take: a tone during each word, silence between, Whisper's words as given."""
    n = int((length or words[-1][2] + 0.4) * SR); a = np.zeros(n, np.float32)
    for _, s, e in words:
        k = np.arange(int(s * SR), int(e * SR)); a[k] = peak * np.sin(2 * np.pi * 220 * k / SR)
    heard = [(x, s, e, E.written(w)) for w, s, e in words for x in E.norm_words(w)]
    t = {"a": a, "sr": SR, "heard": heard, "words": words, "junk": E._cb_junk(a, SR, words), "peak": float(np.abs(a).max()),
         "mos": mos, "mos_min": mos_min, "vsim": sim, "clarity": clarity, "unclear": "it",
         "plan": E._cb_plan(E._to48(a, SR), heard, E.spoken_text(text))}
    return t, E.norm_words(E.spoken_text(text))

def gates(words, text, **kw):
    t, exp = take(words, text, **kw)
    return E._cb_gates(t, exp, (".", "?", "!", ":", ";"))

def spread(text, start=0.1, step=0.32):
    """Whisper's words for a fake take: one every `step` seconds, and a 0.3 s pause after a sentence (as a voice does)."""
    out, t = [], start
    for w in text.split():
        out.append([w, round(t, 3), round(t + step - 0.05, 3)]); t += step + (0.3 if w[-1] in ".?!" else 0.0)
    return out

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

# ---- Shaping a take: silence is the only thing ever changed (28 Nov 2026). These use a real voice (Kokoro's af_heart
# at Chatterbox's 24 kHz) because the faults lived in real consonants: the quiet s of "times", the silent stop in "first".
_RNG = np.random.default_rng(7)

def _kok(text):
    from scipy.signal import resample_poly
    plain, marks = E._marks(text)
    return resample_poly(E.speak(plain, "af_heart", 1.0, 1.0, tuple(marks)).astype(np.float64), 1, 2).astype(np.float32)

def _hiss(sec, db, ref, decay=True):
    """A quiet s or a click: noise above 4 kHz, `db` below the speech level `ref` (rms)."""
    from scipy.signal import butter, sosfilt
    x = sosfilt(butter(4, [4000, 9000], "bp", fs=SR, output="sos"), _RNG.standard_normal(int(sec * SR)))
    x = x / (np.sqrt((x ** 2).mean()) + 1e-9) * ref * 10 ** (db / 20)
    return (x * (np.linspace(1, 0.2, len(x)) if decay else 1)).astype(np.float32)

def _voice_take(chunks, gaps=0.25, shift=0.0, tail=None, inserts=None, one_word=None):
    """A take as Chatterbox gives it: chunks of speech with short natural silences between them, and Whisper's word
    times (spread over each chunk, all moved by `shift`, as Whisper's times can be off). tail=(sec, dB): a quiet s
    on each chunk's end, joined to it like a real one. inserts={gap index: audio} puts a sound in that silence.
    one_word=(i, word): chunks i and i+1 are one word that Whisper hears whole. Returns (take, heard, chunk times)."""
    gaps = gaps if isinstance(gaps, list) else [gaps] * (len(chunks) - 1)
    out, words, t, times = [np.zeros(int(0.15 * SR), np.float32)], [], 0.15, []
    for k, c in enumerate(chunks):
        a = _kok(c)
        if tail:
            ref = float(np.sqrt((a[np.abs(a) > 0.02] ** 2).mean())); a = np.concatenate([a, _hiss(tail[0], tail[1], ref)])
        d = len(a) / SR; ws = c.split()
        new = [[w, round(t + d * i / len(ws) + shift, 3), round(t + d * (i + 1) / len(ws) + shift, 3)] for i, w in enumerate(ws)]
        if one_word and k == one_word[0] + 1:          # the word split across the silence: Whisper hears it whole
            words[-1] = [one_word[1], words[-1][1], new[0][2]]; new = new[1:]
        words += new
        times.append((t, t + d)); out.append(a); t += d
        if k < len(chunks) - 1:
            g = np.zeros(int(gaps[k] * SR), np.float32)
            if inserts and k in inserts:
                x = inserts[k]; m = (len(g) - len(x)) // 2; g[m: m + len(x)] = x
            out.append(g); t += gaps[k]
    out.append(np.zeros(int(0.3 * SR), np.float32))
    heard = [(x, s, e, E.written(w)) for w, s, e in words for x in E.norm_words(w)]
    return np.concatenate(out), heard, times

def _extent(a, sr, thr):
    v = np.flatnonzero(E._vad(E._to48(a, sr), thr)[0]); return (v[-1] - v[0] + 1) * 0.01

def test_quiet_endings_are_kept():       # 28 Nov 2026: "lines", "index", "needs", "times" lost their last sound
    for sents in (["By the end, you'll write it in eight lines."], ["Have I seen it, and how many times?"],
                  ["It will map each value to its index."], ["Walk every index once, and work out the partner this number needs."]):
        a, heard, times = _voice_take(sents, tail=(0.18, -30))
        thr = E._vad(E._to48(a, SR))[1]
        bare = _voice_take(sents)[0]
        assert _extent(a, SR, thr) >= _extent(bare, SR, thr) + 0.12, "the test's quiet s must count as voice"
        out, spans, info = E._cb_assemble(a, SR, heard, sents[0], level=False)
        assert not info.get("unshaped"), info
        assert abs(_extent(out, E.SR, thr) - _extent(a, SR, thr)) <= 0.02, (sents, _extent(out, E.SR, thr), _extent(a, SR, thr))

def test_pause_never_lands_inside_a_word():   # 28 Nov 2026: "Firs … t" and "Re … member" (Whisper's times were off)
    for sents in (["Now it's your turn.", "First, Valid Anagram."], ["Eight needs two.", "Not seen yet.", "Remember eight."]):
        for shift in (-0.35, 0.35):
            a, heard, times = _voice_take(sents, gaps=0.22, shift=shift)
            plan = E._cb_plan(E._to48(a, SR), heard, " ".join(sents))
            assert not plan["joined"], (sents, shift, plan["joined"])
            for b, (x, y) in zip(plan["bounds"], zip(times, times[1:])):
                assert x[1] - 0.05 <= b[0] * 0.01 and b[1] * 0.01 <= y[0] + 0.05, (sents, shift, b, x, y)
            out, spans, info = E._cb_assemble(a, SR, heard, " ".join(sents))
            gaps = [round(q[0] - p[1], 2) for p, q in zip(spans, spans[1:])]
            assert all(g >= E.PAUSE["."] - 0.03 for g in gaps) and not info.get("unshaped"), (gaps, info)
            said, got = _speech_runs(a, SR), _speech_runs(out)         # each sentence in one piece, as long as it was said
            assert len(got) == len(said) == len(sents), (sents, shift, said, got)
            assert all(abs((y - x) - (q - p)) <= 0.02 for (x, y), (p, q) in zip(got, said)), (sents, shift, said, got)

def test_sentences_run_together_are_not_cut():   # no real silence: nothing is inserted, another take is asked for
    sents = ["Now it's your turn.", "First, Valid Anagram."]
    a, heard, times = _voice_take(sents, gaps=0.04)
    plan = E._cb_plan(E._to48(a, SR), heard, " ".join(sents))
    assert plan["joined"] == [0], plan["joined"]
    out, spans, info = E._cb_assemble(a, SR, heard, " ".join(sents), level=False)
    thr = E._vad(E._to48(a, SR))[1]
    assert abs(_extent(out, E.SR, thr) - _extent(a, SR, thr)) <= 0.02          # nothing inserted, nothing lost
    t = {"words": [[h[0], h[1], h[2]] for h in heard], "heard": heard, "junk": False, "peak": 0.5, "mos": 4.3, "mos_min": 4.2,
         "vsim": 0.9, "plan": plan}
    hard, soft = E._cb_gates(t, E.norm_words(" ".join(sents)), (".", "?", "!"))
    assert not hard and any("run together" in x for x in soft), (hard, soft)

def test_pause_after_a_question():         # 27 Nov 2026: "is four here?" ran straight into the next sentence
    sents = ["Now six arrives and asks: is four here?", "You don't search the room.", "Wrong!"]
    a, heard, _ = _voice_take(sents, gaps=0.2)
    out, spans, info = E._cb_assemble(a, SR, heard, " ".join(sents))
    gaps = [round(q[0] - p[1], 2) for p, q in zip(spans, spans[1:])]
    assert gaps[0] >= E.PAUSE["?"] - 0.03 and gaps[1] >= E.PAUSE["."] - 0.03, gaps
    tail = len(out) / E.SR - spans[-1][1]
    assert E.LINE_TAIL <= tail <= E.LINE_TAIL + 0.05, tail

def test_click_between_words_is_caught():     # 28 Nov 2026: a tick between "letter," and "add one"
    chunks = ["For each letter,", "add one if it's there already."]
    ref = float(np.sqrt((_kok(chunks[0]) ** 2).mean()))
    a, heard, _ = _voice_take(chunks, gaps=0.2, inserts={0: _hiss(0.03, -12, ref, decay=False)})
    plan = E._cb_plan(E._to48(a, SR), heard, " ".join(chunks))
    assert [c[1:] for c in plan["clicks"]] == [("letter", "add")], plan["clicks"]
    t, exp = take(spread(" ".join(chunks)), " ".join(chunks)); t["plan"] = plan
    assert any("click" in h for h in E._cb_gates(t, exp, (".", "?", "!"))[0])
    clean, heard2, _ = _voice_take(chunks, gaps=0.2)
    assert not E._cb_plan(E._to48(clean, SR), heard2, " ".join(chunks))["clicks"]

def test_real_consonants_are_not_clicks():    # the t of "yet," after its stop, and a short word like "a", are speech
    for chunks, sound in ((["Not seen yet,", "and we move on."], "t"), (["In C plus plus,", "a", "missing key starts at zero."], None)):
        ref = float(np.sqrt((_kok(chunks[0]) ** 2).mean()))
        ins = {0: _hiss(0.025, -12, ref, decay=False)} if sound else None
        a, heard, _ = _voice_take(chunks, gaps=0.12, inserts=ins)
        plan = E._cb_plan(E._to48(a, SR), heard, " ".join(chunks))
        assert not plan["clicks"] and not plan["stalls"], (chunks, plan["clicks"], plan["stalls"])

def test_stall_inside_a_word_is_caught():     # a word that stops and restarts ("Rem … ember")
    a, heard, _ = _voice_take(["Not seen yet. Re", "member eight."], gaps=0.26, one_word=(0, "Remember"))
    plan = E._cb_plan(E._to48(a, SR), heard, "Not seen yet. Remember eight.")
    assert any(w == "remember" for _, w in plan["stalls"]), (plan["stalls"], heard)
    a2, heard2, _ = _voice_take(["So, to recap,", "one pass."], gaps=0.26)            # a comma pause is not a stall
    assert not E._cb_plan(E._to48(a2, SR), heard2, "So, to recap, one pass.")["stalls"]

def test_clean_lines_raise_nothing():         # no false alarms on clean speech: a false alarm costs a take or a voice switch
    lines = ["Five numbers. Which two add up to ten?", "Think of a party. At the door, you write down every guest who walks in.",
             "Six needs four. And four is in the map, at index two.", "In C plus plus, a missing key already starts at zero.",
             "One pass, and one map lookup per number: O of n time. The map can hold every number, so O of n space too.",
             "Here's the trap: store the number before you check. Take three, two, four, with target six.",
             "Two needs four, not there yet. Four needs two, and two is in the map. One and two. Right."]
    for text in lines:
        sents = [x for x in E._SENT.split(text) if x]
        for shift in (0.0, 0.15, -0.15):
            a, heard, _ = _voice_take(sents, gaps=0.22, shift=shift)
            plan = E._cb_plan(E._to48(a, SR), heard, text)
            out, spans, info = E._cb_assemble(a, SR, heard, text)
            bad = {k: plan[k] for k in ("clicks", "stalls", "joined", "dropped") if plan[k]}
            assert not bad and not info.get("unshaped"), (text, shift, bad, info)

def test_shaping_proof_catches_a_cut():       # if a future change fades into a word, the line goes out unshaped instead
    sents = ["Have I seen it, and how many times?"]
    a, heard, _ = _voice_take(sents, tail=(0.18, -30))
    old = E._edge_fades
    def deep(seg, lead, tail):                 # the old mistake: fading 40 ms into the sentence's own sound
        old(seg, lead + 1920, tail + 1920)
    try:
        E._edge_fades = deep
        out, spans, info = E._cb_assemble(a, SR, heard, sents[0], level=False)
    finally:
        E._edge_fades = old
    thr = E._vad(E._to48(a, SR))[1]
    assert info.get("unshaped") and abs(_extent(out, E.SR, thr) - _extent(a, SR, thr)) <= 0.02, info

def test_unclear_word_goes_back():           # 28 Nov 2026: "start it at one" was blurred though Whisper got the words
    _, soft = gates(spread("or start it at one."), "or start it at one.", clarity=0.2)
    assert any("unclear" in x for x in soft), soft
    _, soft = gates(spread("or start it at one."), "or start it at one.", clarity=0.9)
    assert not soft, soft

def test_lines_are_levelled():
    sents = ["Is four on the list?"]
    a1, h1, _ = _voice_take(sents); a2 = a1 * 3.0
    o1, _, _ = E._cb_assemble(a1, SR, h1, sents[0]); o2, _, _ = E._cb_assemble(a2, SR, h1, sents[0])
    r = lambda a: float(np.sqrt((a[np.abs(a) > 0.01] ** 2).mean()))
    assert abs(20 * np.log10(r(o1) / r(o2))) < 1.0

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

def _line():
    """Three sentences in a real voice with what Chatterbox leaves around them: a breath before the first, a breath and
    a click between sentences, a breath after the last. Each stray sound is at least 0.15 s from the words: closer than
    that it could be part of a word (the s after the stop in "counts", the t of "list"), and those are never cut."""
    from scipy.signal import butter, sosfilt
    rng = np.random.default_rng(0); z = lambda d: np.zeros(int(d * SR), np.float32)
    s1, s2, s3 = _kok("One look."), _kok("Is four here?"), _kok("Yes.")
    ref = float(np.sqrt((s1[np.abs(s1) > 0.02] ** 2).mean()))
    breath = sosfilt(butter(2, 2500, "lp", fs=SR, output="sos"), rng.standard_normal(int(0.12 * SR)))
    breath = (breath / np.sqrt((breath ** 2).mean()) * ref * 10 ** (-32 / 20)).astype(np.float32)
    click = _hiss(0.02, -6, ref, decay=False)
    parts = [z(0.5), breath, z(0.2), s1, z(0.2), breath, z(0.3), click, z(0.3), s2, z(0.13), s3, z(0.2), breath, z(0.1)]
    a = np.concatenate(parts); t = np.cumsum([0] + [len(x) / SR for x in parts])
    (a1, b1), (a2, b2), (a3, b3) = (t[3], t[4]), (t[9], t[10]), (t[11], t[12])
    heard = [("one", a1, (a1 + b1) / 2, False), ("look", (a1 + b1) / 2, b1, False), ("is", a2, a2 + 0.2, False),
             ("four", a2 + 0.2, a2 + 0.45, False), ("here", a2 + 0.45, b2, False), ("yes", a3, b3, False)]
    return a, heard, "One look. Is four here? Yes.", [(a1, b1), (a2, b2), (a3, b3)]

def _speech_runs(b, sr=None):
    """Stretches of voice (10 ms frames, quiet consonants included), merged across gaps under 0.12 s: one per sentence."""
    v = E._vad(E._to48(b, sr or E.SR))[0]; r = E._runs_of(v); out = []
    for s0, s1 in r:
        if out and s0 - out[-1][1] < 12:
            out[-1] = (out[-1][0], s1)
        else:
            out.append((s0, s1))
    return [(x * 0.01, y * 0.01) for x, y in out]

def test_breathing_room_between_sentences():   # 28 Nov 2026: code explanations felt rushed, sentences ran together
    a, heard, text, _ = _line()
    b, spans, _ = E._cb_assemble(a, SR, heard, text)
    runs = _speech_runs(b); gaps = [round(y[0] - x[1], 2) for x, y in zip(runs, runs[1:])]
    assert len(runs) == 3, runs
    assert gaps[0] >= E.PAUSE["."] - 0.03 and gaps[1] >= E.PAUSE["?"] - 0.03, gaps
    assert abs((len(b) / E.SR - runs[-1][1]) - E.LINE_TAIL - 0.02) < 0.04, len(b) / E.SR - runs[-1][1]

def test_no_stray_sounds_or_repeats():        # 28 Nov 2026: bits of breath and noise around "Have I seen it…?"
    a, heard, text, truth = _line()
    b, spans, _ = E._cb_assemble(a, SR, heard, text)
    runs = _speech_runs(b)
    assert len(runs) == 3, runs                                         # no click, breath or fragment survives
    said = [r for r in _speech_runs(a, SR) if any(p <= (r[0] + r[1]) / 2 <= q for p, q in truth)]
    for (x, y), (p, q) in zip(runs, said):                              # every sentence once: nothing cut, nothing doubled
        assert abs((y - x) - (q - p)) <= 0.02, (x, y, p, q)

def test_captions_follow_the_voice():         # spans are exact, not Whisper's estimate
    a, heard, text, _ = _line()
    b, spans, _ = E._cb_assemble(a, SR, heard, text)
    for (x, y), (s0, s1) in zip(_speech_runs(b), spans):
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
