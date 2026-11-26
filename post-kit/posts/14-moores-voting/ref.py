# Reference for post 14 (LeetCode 169). Every value on the slides and in the video comes from here.

def majority_element(nums):
    candidate = None
    count = 0
    for x in nums:
        if count == 0:
            candidate = x   # new candidate
        if x == candidate:
            count = count + 1
        else:
            count = count - 1
    return candidate


def majority_or_none(nums):
    candidate = majority_element(nums)
    return candidate if sum(1 for x in nums if x == candidate) > len(nums) // 2 else None


EXAMPLE = [2, 1, 1, 3, 1]
ANSWER = majority_element(EXAMPLE)
NOMAJ = [1, 2, 3]


def video_steps(nums=EXAMPLE):
    cand, count = None, 0
    steps = [{"eq": ["count =", "0"], "caption": "One candidate, one count."}]
    for i, x in enumerate(nums):
        new = count == 0
        if new:
            cand = x
        count = count + 1 if x == cand else count - 1
        same = [j for j in range(i + 1) if nums[j] == cand]
        if new:
            cap = f"Count is 0, so {x} becomes the candidate."
        elif x == cand:
            cap = f"Another {x}: count goes up."
        else:
            cap = f"{x} differs: it cancels one {cand}."
        steps.append({"ptr": {"x": i}, "gold": [i], "steel": [j for j in same if j != i], "eq": [f"candidate {cand},", f"count {count}"],
                      "chip": f"{cand}: {count}", "chip_hl": new, "caption": cap})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(14)
    cases = ["2 1 1 3 1", "3 2 3", "2 2 1 1 1 2 2", "1", "5 4 4", "-1 -1 2", "1000000000 1000000000 -1000000000"]
    for _ in range(1300):
        n = _r.randint(1, 15)
        m = _r.randint(-9, 9)
        k = n // 2 + 1 + _r.randint(0, n - n // 2 - 1)
        a = [m] * k + [_r.randint(-9, 9) for _ in range(n - k)]
        _r.shuffle(a)
        cases.append(" ".join(map(str, a)))
    a = [7] * 1501 + [_r.randint(-10**9, 10**9) for _ in range(1499)]
    _r.shuffle(a)
    cases.append(" ".join(map(str, a)))
    return cases


def expected(line):
    a = [int(x) for x in line.split()]
    for v in set(a):
        if a.count(v) > len(a) // 2:
            return str(v)
    return "none"
