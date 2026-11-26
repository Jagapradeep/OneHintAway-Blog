# Reference for post 12 (LeetCode 53). Every number on the slides and in the video comes from here.

def max_sub_array(nums):
    current = 0          # sum so far
    best = nums[0]       # largest so far
    for x in nums:
        if current < 0:  # in debt?
            current = 0  # start fresh
        current = current + x
        best = max(best, current)
    return best


def wrong_max_sub_array(nums):
    """The trap: best starts at 0, so an all-negative array returns 0."""
    current, best = 0, 0
    for x in nums:
        if current < 0:
            current = 0
        current += x
        best = max(best, current)
    return best


EXAMPLE = [-2, 3, -1, 4, -7, 5]
BEST = max_sub_array(EXAMPLE)
NEG = [-3, -1, -2]


def video_steps(nums=EXAMPLE):
    current, best, start = 0, nums[0], 0
    steps = [{"eq": ["current =", "0"], "caption": "Carry a running sum. Drop it if it's below 0."}]
    for i, x in enumerate(nums):
        if current < 0:
            steps.append({"frame": [start, i - 1], "dim": list(range(start, i)), "eq": [f"{current} < 0 →", "start fresh"],
                          "caption": "In debt? Drop it and start fresh.", "hold": 0.6})
            current, start = 0, i
        current += x
        best = max(best, current)
        steps.append({"frame": [start, i], "gold": [i], "dim": list(range(start)), "eq": ["current =", str(current)],
                      "chip": str(best), "chip_hl": best == current, "caption": f"Add {x}. Best so far: {best}."})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(12)
    cases = ["-2 3 -1 4 -7 5", "-2 1 -3 4 -1 2 1 -5 4", "1", "5 4 -1 7 8", "-3 -1 -2", "-1", "0 0 0", "10000 -10000 10000", "-10000"]
    for _ in range(1300):
        n = _r.randint(1, 14)
        cases.append(" ".join(str(_r.randint(-10, 10)) for _ in range(n)))
    cases.append(" ".join(str(_r.randint(-10**4, 10**4)) for _ in range(3000)))
    return cases


def expected(line):
    a = [int(x) for x in line.split()]
    pre = [0]
    for x in a:
        pre.append(pre[-1] + x)
    best = a[0]
    for i in range(len(a)):
        pi = pre[i]
        for j in range(i + 1, len(a) + 1):
            if pre[j] - pi > best:
                best = pre[j] - pi
    return str(best)
