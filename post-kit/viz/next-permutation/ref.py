"""Next permutation: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/next-permutation.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "next-permutation"
EXAMPLE = {"nums": [1, 3, 5, 4, 2]}

import itertools


def brute(inp):
    """Every order of the numbers, sorted; the one after the input (wrapping round to the first)."""
    orders = sorted(set(itertools.permutations(inp["nums"])))
    return list(orders[(orders.index(tuple(inp["nums"])) + 1) % len(orders)])


def test_inputs():
    _r.seed(113)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        cases.append({"nums": [_r.randint(0, 4) for _ in range(_r.randint(1, 6))]})
    return cases
