"""Every order of the numbers (LeetCode 46, post 38's backtracking template):
brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/permutations.ts. This
file only says what the right answer is: Python's itertools.permutations, which
lists orders by position in the same order the search saves them.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import itertools
import random as _r

PATTERN = "permutations"
EXAMPLE = {"nums": [1, 2, 3]}


def brute(inp):
    return " | ".join(" ".join(map(str, p)) for p in itertools.permutations(inp["nums"]))


def test_inputs():
    _r.seed(138)
    cases = [dict(EXAMPLE), {"nums": [4]}, {"nums": [2, 2]}, {"nums": [1, 1, 2]}]
    while len(cases) < 1100:
        cases.append({"nums": [_r.randint(0, 9) for _ in range(_r.randint(1, 3))]})
    return cases
