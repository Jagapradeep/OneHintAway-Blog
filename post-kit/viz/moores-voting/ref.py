"""Moore's voting: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/moores-voting.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "moores-voting"
EXAMPLE = {"nums": [2, 2, 1, 1, 1, 2, 2]}

def brute(inp):
    """The number that fills more than half the list, or None when there is none."""
    nums = inp["nums"]
    return next((v for v in sorted(set(nums)) if nums.count(v) * 2 > len(nums)), None)


def test_inputs():
    _r.seed(102)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        n = _r.randint(1, 12)
        nums = [_r.randint(1, 3) for _ in range(n)]
        for i in _r.sample(range(n), _r.randint(n // 2 + 1, n)):   # always a majority: the problem promises one
            nums[i] = 7
        cases.append({"nums": nums})
    return cases
