# Reference for post 23. Every number on the slides and in the video comes from here.

def selection_sort(nums):
    nums = list(nums)
    n = len(nums)
    for i in range(n - 1):
        smallest = i
        for j in range(i + 1, n):
            if nums[j] < nums[smallest]:
                smallest = j
        nums[i], nums[smallest] = nums[smallest], nums[i]
    return nums


def swaps(nums):
    """Swaps that really move something (smallest != i)."""
    nums, total = list(nums), 0
    for i in range(len(nums) - 1):
        smallest = i
        for j in range(i + 1, len(nums)):
            if nums[j] < nums[smallest]:
                smallest = j
        if smallest != i:
            total += 1
        nums[i], nums[smallest] = nums[smallest], nums[i]
    return total


def compares(nums):
    n = len(nums)
    return n * (n - 1) // 2


def wrong_sort(nums):
    """The trap: remember the smallest VALUE, then write it over nums[i]."""
    nums = list(nums)
    n = len(nums)
    for i in range(n - 1):
        smallest = nums[i]
        for j in range(i + 1, n):
            if nums[j] < smallest:
                smallest = nums[j]
        nums[i] = smallest
    return nums


EXAMPLE = [5, 2, 4, 1, 3]
PASSES = len(EXAMPLE) - 1
SWAPS = swaps(EXAMPLE)
COMPARES = compares(EXAMPLE)


def video_steps(nums=EXAMPLE):
    """Each pass: pointer j scans the unsorted part while the smallest so far stays gold, then one swap."""
    a = list(nums)
    n = len(a)
    steps = [{"frame": [0, n - 1], "eq": ["sorted part:", "empty"],
              "caption": "The whole row is unsorted. Find its smallest value."}]
    for i in range(n - 1):
        s = i
        cap = f"Pass {i + 1}: find the smallest unsorted value."
        band = {"band": [0, i - 1, "SORTED PART"]} if i else {}
        for j in range(i + 1, n):
            if a[j] < a[s]:
                eq = [f"{a[j]} < {a[s]} →", "new smallest"]
                s = j
            else:
                eq = [f"{a[j]} {'>' if a[j] > a[s] else '='} {a[s]} →", f"keep {a[s]}"]
            steps.append(dict(band, frame=[i, n - 1], gold=[s], ptr={"j": j}, eq=eq, caption=cap, hold=0.5))
        v = a[s]
        rest = " ".join(map(str, a[i:]))
        step = {"band": [0, i, "SORTED PART"], "gold": [i], "eq": [f"smallest of {rest} →", str(v)]}
        if s != i:
            step["swap"] = [i, s]
            step["chip"] = f"{v}: swap"
            step["chip_hl"] = True
            step["caption"] = f"The {v} swaps with {a[i]} into slot {i}."
        else:
            step["chip"] = f"{v}: stays"
            step["caption"] = f"The {v} is already in slot {i}. No swap."
        a[i], a[s] = a[s], a[i]
        steps.append(step)
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(23)
    cases = ["", "7", "2 1", "4 4 4", "1 2 3 4 5", "5 4 3 2 1", "2147483647 -2147483648 0", "5 2 4 1 3", "3 1 3 1 2"]
    cases.append(" ".join(str(_r.randint(-10**9, 10**9)) for _ in range(1000)))
    for _ in range(1201):
        cases.append(" ".join(str(_r.randint(-20, 20)) for _ in range(_r.randint(0, 12))))
    return cases


def expected(line):
    return " ".join(map(str, sorted(int(x) for x in line.split())))


def insertion_shifts(nums):
    """Shifts insertion sort (post 22) makes on the same input."""
    a, total = list(nums), 0
    for i in range(1, len(a)):
        card, j = a[i], i - 1
        while j >= 0 and a[j] > card:
            a[j + 1] = a[j]; j -= 1; total += 1
        a[j + 1] = card
    return total


def insertion_compares(nums):
    a, total = list(nums), 0
    for i in range(1, len(a)):
        card, j = a[i], i - 1
        while j >= 0:
            total += 1
            if a[j] <= card:
                break
            a[j + 1] = a[j]; j -= 1
        a[j + 1] = card
    return total


SORTED = [1, 2, 3, 4, 5]
