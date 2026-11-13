"""Rotated sorted array: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/rotated-sorted-array.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "rotated-sorted-array"
EXAMPLE = {"nums": [4, 5, 6, 1, 2, 3]}

def brute(inp):
    return min(inp["nums"])


def test_inputs():
    _r.seed(115)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        nums = sorted(_r.sample(range(-30, 31), _r.randint(1, 12)))
        cut = _r.randrange(len(nums))
        cases.append({"nums": nums[cut:] + nums[:cut]})
    return cases
