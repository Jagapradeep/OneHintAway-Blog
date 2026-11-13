"""Merge sort: the merge: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/merge-sort.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "merge-sort"
EXAMPLE = {"left": [1, 4, 7], "right": [2, 3, 9]}

def _rising(n, lo=-20, step=3):
    out, v = [], _r.randint(lo, lo + 10)
    for _ in range(n):
        v += _r.randint(0, step)
        out.append(v)
    return out

def brute(inp):
    return sorted(inp["left"] + inp["right"])


def test_inputs():
    _r.seed(120)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        cases.append({"left": _rising(_r.randint(1, 6)), "right": _rising(_r.randint(1, 6))})
    return cases
