"""Cyclic sort: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/cyclic-sort.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "cyclic-sort"
EXAMPLE = {"nums": [4, 0, 3, 1]}

def brute(inp):
    return next(v for v in range(len(inp["nums"]) + 1) if v not in inp["nums"])


def test_inputs():
    _r.seed(112)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        n = _r.randint(1, 9)
        cases.append({"nums": _r.sample(range(n + 1), n)})
    return cases
