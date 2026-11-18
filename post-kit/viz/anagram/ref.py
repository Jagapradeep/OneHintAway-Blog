"""Valid anagram by frequency count (LeetCode 242, post 36): brute-force answers for
the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/anagram.ts. This file
only says what the right answer is, in the plainest way: sort both words' letters.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "anagram"
EXAMPLE = {"s": "stone", "t": "notes"}


def brute(inp):
    return sorted(inp["s"].lower()) == sorted(inp["t"].lower())


def test_inputs():
    _r.seed(136)
    cases = [dict(EXAMPLE), {"s": "stone", "t": "note"}, {"s": "a", "t": "a"}, {"s": "a", "t": "b"},
             {"s": "Listen", "t": "Silent"}, {"s": "aab", "t": "abb"}, {"s": "abcdefgh", "t": "hgfedcba"}]
    while len(cases) < 1200:
        abc = "abcde" if _r.random() < 0.7 else "abcdefghijklmnopqrstuvwxyz"
        s = "".join(_r.choice(abc) for _ in range(_r.randint(1, 8)))
        if _r.random() < 0.5:
            t = list(s)
            _r.shuffle(t)
            if _r.random() < 0.3 and len(t) > 1:
                t[_r.randrange(len(t))] = _r.choice(abc)
            t = "".join(t)
        else:
            t = "".join(_r.choice(abc) for _ in range(_r.randint(1, 8)))
        cases.append({"s": s, "t": t})
    return cases
