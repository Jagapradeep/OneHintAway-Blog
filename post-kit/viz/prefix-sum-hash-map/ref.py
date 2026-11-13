"""Prefix sum with a hash map: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/prefix-sum-hash-map.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "prefix-sum-hash-map"
EXAMPLE = {"nums": [1, 2, 3, -3, 3], "k": 3}

def brute(inp):
    nums, k = inp["nums"], inp["k"]
    return sum(1 for i in range(len(nums)) for j in range(i + 1, len(nums) + 1) if sum(nums[i:j]) == k)


def test_inputs():
    _r.seed(106)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        cases.append({"nums": [_r.randint(-4, 4) for _ in range(_r.randint(1, 10))], "k": _r.randint(-5, 5)})
    return cases
