# Reference for post 17 (LeetCode 31). Every number on the slides and in the video comes from here.
from itertools import permutations


def next_permutation(nums):
    nums = list(nums)
    n = len(nums)
    i = n - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i = i - 1                # walk left
    if i >= 0:                   # pivot found
        j = n - 1
        while nums[j] <= nums[i]:
            j = j - 1
        nums[i], nums[j] = nums[j], nums[i]
    nums[i + 1:] = reversed(nums[i + 1:])
    return nums


def wrong_next(nums):
    """The trap: stop after the swap, so the tail keeps its biggest order."""
    nums = list(nums)
    n, i = len(nums), len(nums) - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1
    if i >= 0:
        j = n - 1
        while nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
        return nums
    return nums[::-1]


EXAMPLE = [1, 3, 5, 4, 2]
ANSWER = next_permutation(EXAMPLE)
WRONG = wrong_next(EXAMPLE)
EDGE = next_permutation([3, 2, 1])


def video_steps(nums=EXAMPLE):
    a = list(nums)
    n = len(a)
    i = n - 2
    find = "Walk left while the numbers fall."
    steps = [{"eq": ["find the", "pivot"], "caption": find}]
    while i >= 0 and a[i] >= a[i + 1]:
        steps.append({"ptr": {"i": i}, "steel": list(range(i, n)), "eq": [f"{a[i]} ≥ {a[i + 1]} →", "keep walking"], "caption": find})
        i -= 1
    steps.append({"ptr": {"i": i}, "gold": [i], "steel": list(range(i + 1, n)), "eq": [f"{a[i]} < {a[i + 1]} →", "pivot"],
                  "chip": f"pivot {a[i]}", "caption": f"The tail falls. {a[i]} is the pivot."})
    j = n - 1
    swapcap = f"From the right: first number above {a[i]}."
    while a[j] <= a[i]:
        steps.append({"ptr": {"i": i, "j": j}, "gold": [i], "dim": [j], "steel": [k for k in range(i + 1, n) if k != j],
                      "eq": [f"{a[j]} ≤ {a[i]} →", "keep looking"], "caption": swapcap})
        j -= 1
    steps.append({"ptr": {"i": i, "j": j}, "gold": [i, j], "eq": [f"{a[j]} > {a[i]} →", "partner"], "caption": swapcap})
    a[i], a[j] = a[j], a[i]
    steps.append({"swap": [i, j], "ptr": {"i": i, "j": j}, "gold": [i], "steel": list(range(i + 1, n)), "eq": ["swap", f"{a[j]} and {a[i]}"],
                  "chip": f"swap {a[j]}, {a[i]}", "caption": "Swap them. The tail still falls."})
    lo, hi = i + 1, n - 1
    while lo < hi:
        a[lo], a[hi] = a[hi], a[lo]
        steps.append({"swap": [lo, hi], "gold": [i], "band": [i + 1, n - 1, "TAIL"], "eq": ["reverse", "the tail"],
                      "caption": "Reverse the tail into its smallest order."})
        lo += 1; hi -= 1
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(17)
    cases = ["1 3 5 4 2", "1 2 3", "3 2 1", "1 1 5", "1", "2 2 2", "1 5 1", "2 3 1", "100 0 100"]
    for _ in range(1300):
        n = _r.randint(1, 7)
        cases.append(" ".join(str(_r.randint(0, 5)) for _ in range(n)))
    return cases


def expected(line):
    a = tuple(int(x) for x in line.split())
    perms = sorted(set(permutations(a)))
    k = perms.index(a)
    return " ".join(map(str, perms[(k + 1) % len(perms)]))
