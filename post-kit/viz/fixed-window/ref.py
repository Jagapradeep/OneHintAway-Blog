"""Sliding window, fixed size: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/fixed-window.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "fixed-window"
EXAMPLE = {"nums": [2, 1, 5, 1, 3, 2], "k": 3}

def brute(inp):
    nums, k = inp["nums"], inp["k"]
    return max(sum(nums[i:i + k]) for i in range(len(nums) - k + 1))


def test_inputs():
    _r.seed(100)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        n = _r.randint(1, 12)
        cases.append({"nums": [_r.randint(-20, 30) for _ in range(n)], "k": _r.randint(1, n)})
    return cases
