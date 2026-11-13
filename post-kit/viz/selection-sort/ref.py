"""Selection sort: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/selection-sort.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "selection-sort"
EXAMPLE = {"row": [5, 2, 8, 1, 4]}

def brute(inp):
    return sorted(inp["row"])


def test_inputs():
    _r.seed(109)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        cases.append({"row": [_r.randint(-20, 40) for _ in range(_r.randint(1, 9))]})
    return cases
