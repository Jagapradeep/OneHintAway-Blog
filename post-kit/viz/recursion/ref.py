"""Recursion: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/recursion.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "recursion"
EXAMPLE = {"n": 4}

import math


def brute(inp):
    return math.factorial(inp["n"])


def test_inputs():
    _r.seed(119)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        cases.append({"n": _r.randint(0, 10)})
    return cases
