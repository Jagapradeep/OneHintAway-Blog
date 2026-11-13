"""Search a 2D matrix: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/search-2d-matrix.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "search-2d-matrix"
EXAMPLE = {"nums": [1, 3, 5, 7, 9, 11], "cols": 3, "target": 11}

def _rising(n, lo=-20, step=3):
    out, v = [], _r.randint(lo, lo + 10)
    for _ in range(n):
        v += _r.randint(0, step)
        out.append(v)
    return out

def brute(inp):
    return inp["target"] in inp["nums"]


def test_inputs():
    _r.seed(116)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        cols = _r.randint(1, 4)
        nums = _rising(cols * _r.randint(1, 3))
        target = _r.choice(nums) if _r.random() < 0.5 else _r.randint(-22, 30)
        cases.append({"nums": nums, "cols": cols, "target": target})
    return cases
