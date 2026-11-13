"""Prefix sum: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/prefix-sum.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "prefix-sum"
EXAMPLE = {"nums": [3, 1, 4, 1, 5], "left": 1, "right": 3}

def brute(inp):
    return sum(inp["nums"][inp["left"]:inp["right"] + 1])


def test_inputs():
    _r.seed(105)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        n = _r.randint(1, 10)
        left = _r.randint(0, n - 1)
        cases.append({"nums": [_r.randint(-20, 30) for _ in range(n)], "left": left, "right": _r.randint(left, n - 1)})
    return cases
