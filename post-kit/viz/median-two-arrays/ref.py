"""Median of two sorted arrays (LeetCode 4, post 34): brute-force answers for the
website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/median-two-arrays.ts.
This file only says what the right answer is, in the plainest way: put every value
in one sorted list and read the middle.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "median-two-arrays"
EXAMPLE = {"a": [1, 4, 7], "b": [2, 3, 6, 9]}


def brute(inp):
    allv = sorted(inp["a"] + inp["b"])
    n = len(allv)
    return allv[n // 2] if n % 2 else (allv[n // 2 - 1] + allv[n // 2]) / 2


def test_inputs():
    _r.seed(134)
    cases = [dict(EXAMPLE), {"a": [1], "b": [2]}, {"a": [1, 2], "b": [3, 4]}, {"a": [5, 6, 7, 8, 9, 10], "b": [1]},
             {"a": [1, 1, 1], "b": [1, 1, 1]}, {"a": [-99], "b": [99, 99, 99, 99, 99, 99]}]
    while len(cases) < 1300:
        lo, hi = (-5, 5) if _r.random() < 0.4 else (-99, 99)
        cases.append({"a": sorted(_r.randint(lo, hi) for _ in range(_r.randint(1, 6))),
                      "b": sorted(_r.randint(lo, hi) for _ in range(_r.randint(1, 6)))})
    return cases
