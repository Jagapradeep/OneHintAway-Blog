"""Trapping rain water: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/trapping-rain-water.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "trapping-rain-water"
EXAMPLE = {"height": [2, 0, 3, 1, 0, 2, 1, 2]}

def brute(inp):
    h = inp["height"]
    return sum(min(max(h[:i + 1]), max(h[i:])) - h[i] for i in range(len(h)))


def test_inputs():
    _r.seed(118)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        cases.append({"height": [_r.randint(0, 9) for _ in range(_r.randint(1, 12))]})
    return cases
