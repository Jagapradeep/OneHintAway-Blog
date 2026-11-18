"""Subsets (LeetCode 78, post 37): brute-force answers for the website visualizer's
build check.

The step-by-step picture lives in site/visualizer/patterns/subsets.ts. This file
only says what the right answer is, without recursion: every pattern of take /
leave, in the order "take" first, as the search saves them.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import itertools
import random as _r

PATTERN = "subsets"
EXAMPLE = {"nums": [1, 2, 3]}


def brute(inp):
    nums = inp["nums"]
    out = []
    for take in itertools.product([True, False], repeat=len(nums)):
        chosen = [v for v, t in zip(nums, take) if t]
        out.append("[" + " ".join(map(str, chosen)) + "]" if chosen else "[ ]")
    return " ".join(out)


def test_inputs():
    _r.seed(137)
    cases = [dict(EXAMPLE), {"nums": [5]}, {"nums": [0, 0]}, {"nums": [9, 9, 9]}]
    while len(cases) < 1100:
        cases.append({"nums": [_r.randint(0, 9) for _ in range(_r.randint(1, 3))]})
    return cases
