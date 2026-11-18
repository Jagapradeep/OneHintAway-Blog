# Reference for post 34 (LeetCode 4). Every number on the slides and in the video comes from here.
INF = float("inf")


def edge(nums, k, empty):
    if k < 0 or k >= len(nums):
        return empty
    return nums[k]


def median(a, b, trace=None):
    if len(a) > len(b):
        return median(b, a, trace)
    m = len(a)
    n = len(b)
    half = (m + n + 1) // 2
    low = 0
    high = m
    while low < high:
        i = (low + high) // 2
        if trace is not None:
            trace.append((i, half - i, b[half - i - 1], a[i]))
        if b[half - i - 1] > a[i]:
            low = i + 1
        else:
            high = i
    j = half - low
    left_a = edge(a, low - 1, -INF)
    left_b = edge(b, j - 1, -INF)
    left_max = max(left_a, left_b)
    if (m + n) % 2 == 1:
        return left_max
    right_a = edge(a, low, INF)
    right_b = edge(b, j, INF)
    right_min = min(right_a, right_b)
    return (left_max + right_min) / 2


def brute(a, b):
    c = sorted(a + b)
    n = len(c)
    return c[n // 2] if n % 2 else (c[n // 2 - 1] + c[n // 2]) / 2


def show(x):
    return f"{float(x):.1f}"


A = [1, 4, 7]
B = [2, 3, 6, 9]
MERGED = sorted(A + B)
HALF = (len(A) + len(B) + 1) // 2
ANSWER = median(A, B)
TRACE = []
median(A, B, TRACE)
def _cut(a, b):
    t = []
    median(a, b, t)
    lo, hi = 0, len(a)
    half = (len(a) + len(b) + 1) // 2
    while lo < hi:
        i = (lo + hi) // 2
        if b[half - i - 1] > a[i]:
            lo = i + 1
        else:
            hi = i
    return lo


CUT = _cut(A, B)                 # values taken from A
CUT_B = HALF - CUT               # values taken from B


def _clean(steps):
    for st in steps:
        if st.get("gold") and st.get("steel"):
            st["steel"] = [x for x in st["steel"] if x not in st["gold"]]
    return steps


def video_steps(a=A, b=B):
    """Slots 0-2 hold A, slot 3 is a gap, slots 4-7 hold B. A cut is a gap after a slot."""
    off = len(a) + 1
    steps = [{"ghost": [len(a)], "eq": ["left half size =", str(HALF)],
              "caption": "7 values: the left half holds 4 of them."}]
    for i, j, bl, ar in TRACE:
        cuts = ([i - 1] if i > 0 else []) + ([off + j - 1] if j > 0 else [])
        left = list(range(i)) + list(range(off, off + j))
        cap = f"Take {i} from the top row and {j} from the bottom."
        steps.append({"ghost": [len(a)], "cuts": cuts, "steel": left, "eq": [f"{i} + {j} =", str(HALF)],
                      "caption": cap, "quick": True})
        ok = not bl > ar
        steps.append({"ghost": [len(a)], "cuts": cuts, "steel": left, "gold": [off + j - 1, i],
                      "eq": [f"{bl} > {ar} →", "take more from top"] if not ok else [f"{bl} ≤ {ar} →", "the cut fits"],
                      "caption": cap, "chip": f"{i}: {'no' if not ok else 'fits'}", "chip_hl": ok})
    i, j = CUT, CUT_B
    cuts = [i - 1, off + j - 1]
    left = list(range(i)) + list(range(off, off + j))
    steps.append({"ghost": [len(a)], "cuts": cuts, "steel": left, "gold": [i - 1, off + j],
                  "eq": [f"{a[i - 1]} ≤ {b[j]} →", "the other side fits too"],
                  "caption": "Every left value ≤ every right value."})
    steps.append({"ghost": [len(a)], "cuts": cuts, "steel": left, "gold": [i - 1, off + j - 1],
                  "eq": [f"max({a[i - 1]}, {b[j - 1]}) =", str(max(a[i - 1], b[j - 1]))],
                  "caption": "Odd total: the median is the left max."})
    return _clean(steps)


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def _line(a, b):
    return " ".join(map(str, a)) + "|" + " ".join(map(str, b))


def test_inputs():
    _r.seed(34)
    M = 10**6
    cases = [(A, B), ([1, 3], [2]), ([1, 2], [3, 4]), ([], [1]), ([2], []), ([], [2, 3]), ([5], [5]),
             ([1, 1, 1], [1, 1, 1]), ([-M], [M]), ([M] * 1000, [-M] * 1000), ([1, 2, 3], [4, 5, 6, 7, 8]),
             ([10, 20], [1, 2, 3, 4, 5, 6]), ([-5, -3, -1], [-4, -2])]
    cases.append((sorted(_r.randint(-M, M) for _ in range(1000)), sorted(_r.randint(-M, M) for _ in range(1000))))
    cases.append((sorted(_r.randint(-M, M) for _ in range(3)), sorted(_r.randint(-M, M) for _ in range(1000))))
    for _ in range(1300):
        m, n = _r.randint(0, 7), _r.randint(0, 7)
        if m + n == 0:
            n = 1
        cases.append((sorted(_r.randint(-20, 20) for _ in range(m)), sorted(_r.randint(-20, 20) for _ in range(n))))
    return [_line(a, b) for a, b in cases]


def expected(line):
    x, y = line.split("|")
    return show(brute([int(v) for v in x.split()], [int(v) for v in y.split()]))
