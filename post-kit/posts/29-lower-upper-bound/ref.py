# Reference for post 29. Every number on the slides and in the video comes from here.
import bisect


def lower_bound(nums, target):
    low = 0
    high = len(nums)
    while low < high:
        middle = (low + high) // 2
        if nums[middle] < target:
            low = middle + 1
        else:
            high = middle
    return low


def upper_bound(nums, target):
    return lower_bound(nums, target + 1)


def first_match_search(nums, target):
    """The trap: post 28's search stops at any match, not the first."""
    low, high = 0, len(nums) - 1
    while low <= high:
        middle = (low + high) // 2
        if nums[middle] == target:
            return middle
        elif nums[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1


def search_range(nums, target):
    first = lower_bound(nums, target)
    after = lower_bound(nums, target + 1)
    return [-1, -1] if first == after else [first, after - 1]


EXAMPLE = [1, 2, 2, 2, 4, 5]
TARGET = 2
LOWER = lower_bound(EXAMPLE, TARGET)
UPPER = upper_bound(EXAMPLE, TARGET)
COUNT = UPPER - LOWER


def runs(nums, target, label):
    low, high = 0, len(nums)
    out = []
    while low < high:
        m = (low + high) // 2
        v = nums[m]
        st = {"frame": [low, high - 1], "gold": [m]}
        if v < target:
            st.update({"eq": [f"{label}: {v} < {target} →", "go right"], "chip": f"{v} < {target}",
                       "caption": f"{v} < {target}: the answer is right of slot {m}."})
            low = m + 1
        else:
            st.update({"eq": [f"{label}: {v} ≥ {target} →", "keep it"], "chip": f"{v} ≥ {target}",
                       "caption": f"{v} ≥ {target}: slot {m} may be it, so keep it."})
            high = m
        out.append(st)
    return out, low


def video_steps(nums=EXAMPLE, target=TARGET):
    a, lo = runs(nums, target, "find 2")
    b, up = runs(nums, target + 1, "find 3")
    a[-1]["caption"] = f"{a[-1]['caption'].split(':')[0]}: low meets high at slot {lo}."
    b[-1]["caption"] = f"{b[-1]['caption'].split(':')[0]}: low meets high at slot {up}."
    return [{"frame": [0, len(nums) - 1], "eq": ["lowerBound(2)", "?"],
             "caption": "Find the first slot whose value is at least 2."}] + a + b


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(29)
    cases = ["2|1 2 2 2 4 5", "3|1 2 2 2 4 5", "6|1 2 2 2 4 5", "0|1 2 2 2 4 5", "1|1 2 2 2 4 5", "5|1 2 2 2 4 5",
             "8|5 7 7 8 8 10", "6|5 7 7 8 8 10", "0|", "4|4", "3|4", "5|4", "7|7 7 7 7", "-1000000000|-1000000000 1000000000",
             "1000000000|-1000000000 1000000000"]
    big = sorted(_r.randint(-1000, 1000) for _ in range(100000))
    cases.append(f"{big[50000]}|" + " ".join(map(str, big)))
    for _ in range(1200):
        n = _r.randint(0, 15)
        a = sorted(_r.randint(-8, 8) for _ in range(n))
        cases.append(f"{_r.randint(-10, 10)}|" + " ".join(map(str, a)))
    return cases


def expected(line):
    t, rest = line.split("|")
    a = [int(x) for x in rest.split()]
    t = int(t)
    return f"{bisect.bisect_left(a, t)} {bisect.bisect_left(a, t + 1)}"


def count_of(nums, t):
    return lower_bound(nums, t + 1) - lower_bound(nums, t)
