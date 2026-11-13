"""Binary search on answers: brute-force answers for the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/binary-search-on-answers.ts. This file only says
what the right answer is, in the plainest way possible, so the two are written independently.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r

PATTERN = "binary-search-on-answers"
EXAMPLE = {"piles": [3, 6, 7, 11], "hours": 8}

def brute(inp):
    piles, hours = inp["piles"], inp["hours"]
    return next(s for s in range(1, max(piles) + 1) if sum(-(-p // s) for p in piles) <= hours)


def test_inputs():
    _r.seed(117)
    cases = [dict(EXAMPLE)]
    for _ in range(1200):
        piles = [_r.randint(1, 12) for _ in range(_r.randint(1, 6))]
        cases.append({"piles": piles, "hours": len(piles) + _r.randint(0, 14)})
    return cases
