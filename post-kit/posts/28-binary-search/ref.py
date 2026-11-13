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
