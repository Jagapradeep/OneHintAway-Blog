"""Three-way partition: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/three-way-partition.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "three-way-partition"
EXAMPLE = {"nums": [2, 0, 2, 1, 1, 0]}

def brute(inp):
    return sorted(inp["nums"])


def test_inputs():
    _r.seed(111)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        cases.append({"nums": [_r.randint(0, 2) for _ in range(_r.randint(1, 12))]})
    return cases
