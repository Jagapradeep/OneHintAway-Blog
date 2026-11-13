"""Lower bound: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/lower-bound.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "lower-bound"
EXAMPLE = {"nums": [1, 2, 2, 2, 4, 5], "target": 2}

def _rising(n, lo=-20, step=3):
    out, v = [], _r.randint(lo, lo + 10)
    for _ in range(n):
        v += _r.randint(0, step)
        out.append(v)
    return out

def brute(inp):
    return next((i for i, v in enumerate(inp["nums"]) if v >= inp["target"]), len(inp["nums"]))


def test_inputs():
    _r.seed(114)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        cases.append({"nums": _rising(_r.randint(0, 12)), "target": _r.randint(-22, 30)})
    return cases
