# Reference for post 28 (LeetCode 704). Every number on the slides and in the video comes from here.

def binary_search(nums, target):
    low = 0
    high = len(nums) - 1
    while low <= high:
        middle = low + (high - low) // 2
        if nums[middle] == target:
            return middle
        elif nums[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1


def wrong_search(nums, target):
    """The trap: while low < high skips the last one-value range."""
    low, high = 0, len(nums) - 1
    while low < high:
        middle = low + (high - low) // 2
        if nums[middle] == target:
            return middle
        elif nums[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1


def checks(nums, target):
    low, high, c = 0, len(nums) - 1, 0
    while low <= high:
        c += 1
        middle = low + (high - low) // 2
        if nums[middle] == target:
            return c
        elif nums[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return c


EXAMPLE = [1, 3, 5, 7, 9, 11]
TARGET = 7
FOUND = binary_search(EXAMPLE, TARGET)
CHECKS = checks(EXAMPLE, TARGET)
MAX_CHECKS = (10**6).bit_length()      # at most this many checks for 1,000,000 values


def video_steps(nums=EXAMPLE, target=TARGET):
    low, high = 0, len(nums) - 1
    steps = [{"frame": [low, high], "ptr": {"low": low, "high": high}, "eq": ["target =", str(target)],
              "caption": f"Look for {target}. The answer can be anywhere from low to high."}]
    while low <= high:
        m = low + (high - low) // 2
        v = nums[m]
        dim = [i for i in range(len(nums)) if i < low or i > high]
        st = {"frame": [low, high], "gold": [m], "ptr": {"low": low, "high": high}}
        if dim:
            st["dim"] = dim
        if v == target:
            st.update({"eq": [f"middle {m}: {v} =", "found"], "chip": f"{v} = {target}", "chip_hl": True,
                       "caption": f"nums[{m}] is {target}. Return {m}."})
            steps.append(st)
            break
        if v < target:
            st.update({"eq": [f"{v} < {target} →", "go right"], "chip": f"{v} < {target}",
                       "caption": f"{v} is too small, so the left half goes: low = {m + 1}."})
            low = m + 1
        else:
            st.update({"eq": [f"{v} > {target} →", "go left"], "chip": f"{v} > {target}",
                       "caption": f"{v} is too big, so the right half goes: high = {m - 1}."})
            high = m - 1
        steps.append(st)
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(28)
    cases = ["5|5", "4|5", "6|5", "7|1 3 5 7 9 11", "11|1 3 5 7 9 11", "1|1 3 5 7 9 11", "4|1 3 5 7 9 11",
             "0|1 3 5 7 9 11", "12|1 3 5 7 9 11", "-9999|-9999 9999", "9999|-9999 9999", "0|-9999 9999"]
    big = sorted(_r.sample(range(-9999, 10000), 10000))
    cases.append(f"{big[6789]}|" + " ".join(map(str, big)))
    cases.append("10000|" + " ".join(map(str, big)))
    for _ in range(1200):
        n = _r.randint(1, 15)
        a = sorted(_r.sample(range(-30, 31), n))
        t = _r.choice(a) if _r.random() < 0.6 else _r.randint(-32, 32)
        cases.append(f"{t}|" + " ".join(map(str, a)))
    return cases


def expected(line):
    t, rest = line.split("|")
    a = [int(x) for x in rest.split()]
    t = int(t)
    return str(a.index(t) if t in a else -1)


def max_checks(n):
    return n.bit_length()
