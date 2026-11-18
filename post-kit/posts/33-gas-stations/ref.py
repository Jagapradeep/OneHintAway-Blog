# Reference for post 33 (GFG Minimize Max Distance to Gas Station). Every number on the slides comes from here.
import math
import heapq
from fractions import Fraction


def pumps_needed(stations, d):
    count = 0
    for i in range(1, len(stations)):
        gap = stations[i] - stations[i - 1]
        count = count + math.ceil(gap / d) - 1
    return count


def min_max_gap(stations, k, trace=None):
    n = len(stations)
    low = 0.0
    high = float(stations[n - 1] - stations[0])
    while high - low > 0.000001:
        d = (low + high) / 2
        need = pumps_needed(stations, d)
        if trace is not None:
            trace.append((low, high, d, need))
        if need <= k:
            high = d
        else:
            low = d
    return high


def exact(stations, k):
    """Brute force: hand out pumps one at a time to the gap whose pieces are longest
    right now, splitting that gap evenly. Exact fractions."""
    gaps = [stations[i] - stations[i - 1] for i in range(1, len(stations))]
    if not gaps:
        return Fraction(0)
    heap = [(-Fraction(g), g, 0) for g in gaps]
    heapq.heapify(heap)
    for _ in range(k):
        _, g, c = heapq.heappop(heap)
        heapq.heappush(heap, (-Fraction(g, c + 2), g, c + 1))
    return -heap[0][0]


def two_dp(fr):
    q = fr * 100
    r = math.floor(q + Fraction(1, 2))
    return f"{r // 100}.{r % 100:02d}"


def fmt(x):
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return s


def longest(gaps, shares):
    return fmt(max(g / (s + 1) for g, s in zip(gaps, shares)))


STATIONS = [1, 3, 12, 16]
K = 3
GAPS = [STATIONS[i] - STATIONS[i - 1] for i in range(1, len(STATIONS))]
ROAD = STATIONS[-1] - STATIONS[0]
ANSWER = two_dp(exact(STATIONS, K))
TRACE = []
min_max_gap(STATIONS, K, TRACE)
ROUNDS = len(TRACE)


def video_steps(stations=STATIONS, k=K):
    gaps = [stations[i] - stations[i - 1] for i in range(1, len(stations))]
    steps = [{"eq": ["pumps allowed:", str(k)],
              "caption": f"Gaps {', '.join(map(str, gaps))}. Find the smallest d."}]
    for low, high, d, need in TRACE[:6]:
        cap = f"Range {fmt(low)} to {fmt(high)}. Try d = {fmt(d)}."
        steps.append({"eq": ["try d =", fmt(d)], "caption": cap, "quick": True})
        per = [math.ceil(g / d) - 1 for g in gaps]
        long_ones = [i for i, g in enumerate(gaps) if g > d]
        verdict = "fits: go lower" if need <= k else "too many: go higher"
        steps.append({"gold": long_ones, "eq": [f"{' + '.join(map(str, per))} = {need} →", verdict],
                      "caption": cap, "chip": f"{fmt(d)}: {need}", "chip_hl": need <= k})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def _ambiguous(stations, k):
    """The search returns a value in [answer, answer + 0.000001]. Skip the rare inputs where
    a rounding tie (x.xx5) sits in that window, so every language prints the same 2 decimals."""
    a = exact(stations, k)
    lo, hi = a * 100 - Fraction(1, 10**7), (a + Fraction(2, 10**6)) * 100
    return math.floor(lo + Fraction(1, 2)) != math.floor(hi + Fraction(1, 2))


def _line(stations, k):
    return f"{k}|" + " ".join(map(str, stations))


def test_inputs():
    _r.seed(33)
    cases = [(STATIONS, K), (STATIONS, 0), (STATIONS, 1), ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 9),
             ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 1), ([3, 6, 7, 8, 10], 3), ([0, 10**9], 0), ([0, 10**9], 99999),
             ([0, 1], 100000), ([0, 7], 2)]
    big = sorted(_r.sample(range(0, 10**9 + 1), 5000))
    cases.append((big, 100000))
    cases.append((list(range(0, 5000 * 200000, 200000)), 77777))
    for _ in range(1300):
        n = _r.randint(2, 8)
        st = sorted(_r.sample(range(0, 60), n))
        cases.append((st, _r.randint(0, 12)))
    for _ in range(40):
        n = _r.randint(2, 30)
        st = sorted(_r.sample(range(0, 10**9 + 1), n))
        cases.append((st, _r.randint(0, 1000)))
    return [_line(s, k) for s, k in cases if not _ambiguous(s, k)]


def expected(line):
    k, rest = line.split("|")
    return two_dp(exact([int(x) for x in rest.split()], int(k)))
