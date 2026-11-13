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
              "caption": "Find the drop: compare middle with last."}]
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


# ---- video dressing: LOW / MID / HIGH labels, discarded side dimmed ----
def _dress(steps, n):
    for st in steps:
        fr = st.get("frame")
        if not fr:
            continue
        lo, hi = fr
        out = [i for i in range(n) if i < lo or i > hi]
        if out:
            st["dim"] = sorted(set(st.get("dim", []) + out))
        old = st.get("ptr") or {}
        ptr = {"low": old.get("low", lo)}
        if st.get("gold"):
            ptr["mid"] = st["gold"][0]
        ptr["high"] = old.get("high", hi)
        st["ptr"] = ptr
    return steps


def _narrow(steps):
    """After each check, a short step of its own: the range shrinks before the next middle appears."""
    out = []
    for k, st in enumerate(steps):
        out.append(st)
        nx = steps[k + 1] if k + 1 < len(steps) else None
        if not (nx and st.get("gold") and st.get("frame") and nx.get("frame")) or nx["frame"] == st["frame"]:
            continue
        (a, b), (c, d) = st["frame"], nx["frame"]
        if c < a or d > b:                  # a new search starts: not a shrink
            continue
        mid = {"frame": [c, d], "eq": st["eq"], "caption": st["caption"], "hold": 0.5}
        if st.get("steel") == [b]:
            mid["steel"] = [d]
        out.append(mid)
    return out


_raw_video_steps = video_steps


def video_steps(*args, **kw):
    return _dress(_narrow(_raw_video_steps(*args, **kw)), len(EXAMPLE))


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
