"""Hashing: two sum: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/hash-two-sum.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "hash-two-sum"
EXAMPLE = {"nums": [3, 8, 11, 6, 2], "target": 8}

def brute(inp):
    nums, target = inp["nums"], inp["target"]
    for j in range(len(nums)):
        for i in range(j):
            if nums[i] + nums[j] == target:
                return [i, j]
    return None


def test_inputs():
    _r.seed(104)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        nums = [_r.randint(-10, 10) for _ in range(_r.randint(1, 10))]
        cases.append({"nums": nums, "target": _r.randint(-20, 20)})
    return cases
