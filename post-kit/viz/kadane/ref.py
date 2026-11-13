"""Kadane's algorithm: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/kadane.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "kadane"
EXAMPLE = {"nums": [4, -6, 3, -1, 5, -9, 2]}

def brute(inp):
    nums = inp["nums"]
    return max(sum(nums[i:j]) for i in range(len(nums)) for j in range(i + 1, len(nums) + 1))


def test_inputs():
    _r.seed(101)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        cases.append({"nums": [_r.randint(-20, 20) for _ in range(_r.randint(1, 12))]})
    return cases
