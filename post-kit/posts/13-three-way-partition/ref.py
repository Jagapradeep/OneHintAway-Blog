# Reference for post 13 (LeetCode 75). Every number on the slides and in the video comes from here.

def sort_colors(nums):
    nums = list(nums)
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
    return nums


def wrong_sort_colors(nums):
    """The trap: mid also moves after the swap with high, so the number that came back is never checked."""
    nums = list(nums)
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
            mid += 1
    return nums


def loop_steps(nums):
    nums = list(nums)
    low, mid, high, c = 0, 0, len(nums) - 1, 0
    while mid <= high:
        c += 1
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]; low += 1; mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:
            nums[mid], nums[high] = nums[high], nums[mid]; high -= 1
    return c


EXAMPLE = [1, 0, 2, 2, 1, 0]
SORTED = sort_colors(EXAMPLE)
STEPS = loop_steps(EXAMPLE)
TRAP = [1, 2, 0]


def video_steps(nums=EXAMPLE):
    a = list(nums)
    low, mid, high = 0, 0, len(a) - 1
    steps = [{"ptr": {"low": low, "mid": mid, "high": high}, "eq": ["check", f"nums[{mid}]"], "caption": "0s to the front, 2s to the back."}]
    while mid <= high:
        v = a[mid]
        if v == 0:
            st = {"swap": [low, mid]} if low != mid else {}
            a[low], a[mid] = a[mid], a[low]
            low += 1; mid += 1
            steps.append(dict(st, ptr={"low": low, "mid": min(mid, len(a) - 1), "high": high}, steel=list(range(low)) + list(range(high + 1, len(a))),
                              eq=["0 →", "swap with low"], caption="A 0 goes to the low end."))
        elif v == 1:
            mid += 1
            steps.append({"ptr": {"low": low, "mid": min(mid, len(a) - 1), "high": high}, "steel": list(range(low)) + list(range(high + 1, len(a))),
                          "eq": ["1 →", "leave it"], "caption": "A 1 stays in the middle."})
        else:
            st = {"swap": [mid, high]} if mid != high else {}
            a[mid], a[high] = a[high], a[mid]
            high -= 1
            steps.append(dict(st, ptr={"low": low, "mid": mid, "high": max(high, 0)}, steel=list(range(low)) + list(range(high + 1, len(a))),
                              gold=[mid] if mid <= high else [], eq=["2 →", "swap with high"], caption="A 2 goes back; check what came in."))
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(13)
    cases = ["1 0 2 2 1 0", "2 0 2 1 1 0", "2 0 1", "0", "1", "2", "1 2 0", "0 0 0", "2 2 2", "1 1 1", "2 1 0"]
    for _ in range(1300):
        cases.append(" ".join(str(_r.randint(0, 2)) for _ in range(_r.randint(1, 14))))
    cases.append(" ".join(str(_r.randint(0, 2)) for _ in range(300)))
    return cases


def expected(line):
    return " ".join(map(str, sorted(int(x) for x in line.split())))
