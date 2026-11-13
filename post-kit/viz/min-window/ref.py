"""Minimum window substring: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/min-window.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "min-window"
EXAMPLE = {"s": "ADOBECBA", "t": "ABC"}

def brute(inp):
    s, t = inp["s"], inp["t"]
    for size in range(len(t), len(s) + 1):
        for i in range(len(s) - size + 1):
            piece = s[i:i + size]
            if all(piece.count(c) >= t.count(c) for c in set(t)):
                return piece
    return ""


def test_inputs():
    _r.seed(103)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        s = "".join(_r.choice("ABCD") for _ in range(_r.randint(1, 10)))
        t = "".join(_r.choice("ABCDE" if _r.random() < 0.2 else "ABC") for _ in range(_r.randint(1, 4)))
        cases.append({"s": s, "t": t})
    return cases
