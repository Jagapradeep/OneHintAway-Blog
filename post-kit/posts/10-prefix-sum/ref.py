# Reference for post 10 (LeetCode 303). Every number on the slides and in the video comes from here.

def build_prefix(nums):
    n = len(nums)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + nums[i]
    return prefix


def range_sum(prefix, left, right):
    return prefix[right + 1] - prefix[left]


def wrong_range_sum(prefix, left, right):
    """The trap: forget the shift by one."""
    return prefix[right] - prefix[left]


EXAMPLE = [3, 1, 4, 1, 5]
PREFIX = build_prefix(EXAMPLE)
Q1 = range_sum(PREFIX, 1, 3)
Q2 = range_sum(PREFIX, 2, 4)
WRONG = wrong_range_sum(PREFIX, 1, 3)


def video_steps(nums=EXAMPLE):
    p = build_prefix(nums)
    cap = "Each box becomes the sum so far."
    steps = [{"eq": ["start:", "0"], "caption": cap},
             {"gold": [0], "eq": [f"0 + {nums[0]} =", str(p[1])], "caption": cap}]
    for i in range(1, len(nums)):
        steps.append({"set": {str(i): p[i + 1]}, "gold": [i], "steel": list(range(i)), "eq": [f"{p[i]} + {nums[i]} =", str(p[i + 1])], "caption": cap})
    steps.append({"gold": [3], "steel": [0], "eq": [f"{p[4]} − {p[1]} =", str(Q1)], "chip": f"1..3 = {Q1}", "caption": "Sum of index 1 to 3: one subtraction."})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(10)
    cases = ["3 1 4 1 5 | 1 3, 2 4, 0 4, 0 0", "-2 0 3 -5 2 -1 | 0 2, 2 5, 0 5", "7 | 0 0", "100000 -100000 | 0 1, 1 1"]
    for _ in range(1300):
        n = _r.randint(1, 12)
        a = [_r.randint(-50, 50) for _ in range(n)]
        qs = []
        for _ in range(_r.randint(1, 5)):
            l = _r.randrange(n); r = _r.randrange(l, n)
            qs.append(f"{l} {r}")
        cases.append(" ".join(map(str, a)) + " | " + ", ".join(qs))
    big = [_r.randint(-10**5, 10**5) for _ in range(10000)]
    qs = [f"{l} {r}" for l, r in ((0, 9999), (17, 8000), (5000, 5000), (123, 9876))]
    cases.append(" ".join(map(str, big)) + " | " + ", ".join(qs))
    return cases


def expected(line):
    a, q = line.split("|")
    a = [int(x) for x in a.split()]
    out = []
    for pair in q.split(","):
        l, r = map(int, pair.split())
        out.append(str(sum(a[l:r + 1])))
    return " ".join(out)
