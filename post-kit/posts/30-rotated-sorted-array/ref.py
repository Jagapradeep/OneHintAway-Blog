# Reference for post 30 (LeetCode 153). Every number on the slides and in the video comes from here.

def find_min_index(nums):
    low = 0
    high = len(nums) - 1
    while low < high:
        middle = (low + high) // 2
        if nums[middle] > nums[high]:
            low = middle + 1
        else:
            high = middle
    return low


def find_min(nums):
    return nums[find_min_index(nums)]


def wrong_find_min(nums):
    """The trap: compare the middle with nums[low] instead of nums[high]."""
    low, high = 0, len(nums) - 1
    while low < high:
        middle = (low + high) // 2
        if nums[middle] > nums[low]:
            low = middle + 1
        else:
            high = middle
    return nums[low]


def sorted_half(nums, low, high):
    middle = (low + high) // 2
    return "left" if nums[low] <= nums[middle] else "right"


EXAMPLE = [4, 5, 6, 1, 2, 3]
MIN = find_min(EXAMPLE)
MIN_AT = find_min_index(EXAMPLE)


def video_steps(nums=EXAMPLE):
    low, high = 0, len(nums) - 1
    steps = [{"frame": [low, high], "steel": [high], "eq": ["compare middle with", f"last = {nums[high]}"],
              "caption": "The minimum is where the order breaks. Compare the middle with the last value."}]
    while low < high:
        m = (low + high) // 2
        st = {"frame": [low, high], "gold": [m], "steel": [high]}
        if nums[m] > nums[high]:
            st.update({"eq": [f"{nums[m]} > {nums[high]} →", "drop is right"], "chip": f"{nums[m]} > {nums[high]}",
                       "caption": f"{nums[m]} > {nums[high]}: the drop is right of slot {m}. low = {m + 1}."})
            low = m + 1
        else:
            st.update({"eq": [f"{nums[m]} < {nums[high]} →", "keep middle"], "chip": f"{nums[m]} < {nums[high]}",
                       "caption": f"{nums[m]} < {nums[high]}: the minimum is here or left. high = {m}."})
            high = m
        steps.append(st)
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(30)
    cases = ["7", "2 1", "1 2", "4 5 6 1 2 3", "3 4 5 1 2", "4 5 6 7 0 1 2", "11 13 15 17", "6 7 1 2 3 4 5",
             "5 1 2 3 4", "2 3 4 5 1", "-5000 5000", "5000 -5000"]
    base = sorted(_r.sample(range(-5000, 5001), 5000))
    r = _r.randint(0, 4999)
    cases.append(" ".join(map(str, base[r:] + base[:r])))
    for _ in range(1200):
        n = _r.randint(1, 15)
        a = sorted(_r.sample(range(-40, 41), n))
        r = _r.randint(0, n - 1)
        cases.append(" ".join(map(str, a[r:] + a[:r])))
    return cases


def expected(line):
    return str(min(int(x) for x in line.split()))
