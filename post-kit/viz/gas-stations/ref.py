"""Minimise the largest gap after adding k pumps (post 33): brute-force answers for
the website visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/gas-stations.ts. This
file only says what the right answer is, in the plainest way: try every way of
sharing the k pumps among the gaps (each gap split evenly), with exact fractions.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import random as _r
from fractions import Fraction

PATTERN = "gas-stations"
EXAMPLE = {"stations": [1, 3, 12, 16], "k": 3}


def _shares(k, parts):
    """Every way to write k as an ordered sum of `parts` whole numbers from 0."""
    if parts == 1:
        yield (k,)
        return
    for first in range(k + 1):
        for rest in _shares(k - first, parts - 1):
            yield (first,) + rest


def brute(inp):
    st, k = inp["stations"], inp["k"]
    gaps = [b - a for a, b in zip(st, st[1:])]
    best = min(max(Fraction(g, p + 1) for g, p in zip(gaps, share)) for share in _shares(k, len(gaps)))
    return float(best)


def test_inputs():
    _r.seed(133)
    cases = [dict(EXAMPLE), {"stations": [0, 99], "k": 0}, {"stations": [0, 99], "k": 9},
             {"stations": [0, 1, 2, 3, 4, 5], "k": 9}, {"stations": [5, 6], "k": 4}]
    while len(cases) < 1200:
        n = _r.randint(2, 6)
        st = sorted(_r.sample(range(100), n))
        cases.append({"stations": st, "k": _r.randint(0, 9)})
    return cases
