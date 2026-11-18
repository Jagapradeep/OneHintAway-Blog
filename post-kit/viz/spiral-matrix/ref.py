"""Spiral order (LeetCode 54, post 35): brute-force answers for the website
visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/spiral-matrix.ts. This
file only says what the right answer is, a different way: take the top row, turn
what is left a quarter to the left, and repeat.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "spiral-matrix"
EXAMPLE = {"nums": list(range(1, 13)), "cols": 4}


def brute(inp):
    nums, cols = inp["nums"], inp["cols"]
    grid = [nums[r:r + cols] for r in range(0, len(nums), cols)]
    out = []
    while grid:
        out += grid[0]
        grid = [list(row) for row in zip(*grid[1:])][::-1]
    return out


def test_inputs():
    _r.seed(135)
    cases = [dict(EXAMPLE), {"nums": [7], "cols": 1}, {"nums": [1, 2, 3, 4], "cols": 4}, {"nums": [1, 2, 3, 4], "cols": 1},
             {"nums": [1, 2, 3, 4, 5, 6], "cols": 3}, {"nums": list(range(1, 10)), "cols": 3}]
    while len(cases) < 1200:
        cols = _r.randint(1, 4)
        rows = _r.randint(1, min(4, 12 // cols))
        cases.append({"nums": [_r.randint(-99, 99) for _ in range(rows * cols)], "cols": cols})
    return cases
