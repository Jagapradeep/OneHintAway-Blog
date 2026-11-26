# Reference for post 15 (LeetCode 268). Every number on the slides and in the video comes from here.

def missing_number(nums):
    nums = list(nums)
    n = len(nums)
    i = 0
    while i < n:
        seat = nums[i]
        if seat < n and nums[seat] != seat:
            nums[i], nums[seat] = nums[seat], nums[i]
        else:
            i = i + 1          # home, or no seat
    for i in range(n):
        if nums[i] != i:       # wrong number
            return i
    return n


def seated(nums):
    nums = list(nums)
    n, i, swaps, skips = len(nums), 0, 0, 0
    while i < n:
        seat = nums[i]
        if seat < n and nums[seat] != seat:
            nums[i], nums[seat] = nums[seat], nums[i]
            swaps += 1
        else:
            skips += seat >= n
            i += 1
    return nums, swaps, skips


def wrong_missing(nums):
    """The trap: no seat < n check, so the number n looks up a seat that doesn't exist."""
    nums = list(nums)
    n, i = len(nums), 0
    try:
        while i < n:
            seat = nums[i]
            if nums[seat] != seat:
                nums[i], nums[seat] = nums[seat], nums[i]
            else:
                i += 1
    except IndexError:
        return f"crash: nums[{seat}]"
    return next((k for k in range(n) if nums[k] != k), n)


EXAMPLE = [3, 0, 4, 1, 5]
ANSWER = missing_number(EXAMPLE)
AFTER, SWAPS, SKIPS = seated(EXAMPLE)


def video_steps(nums=EXAMPLE):
    a = list(nums)
    n, i = len(a), 0
    cap = "Send each number to its own seat."
    steps = [{"ptr": {"i": 0}, "eq": ["seat of x =", "x"], "caption": cap}]
    while i < n:
        x = a[i]
        if x < n and a[x] != x:
            a[i], a[x] = a[x], a[i]
            steps.append({"swap": [i, x], "ptr": {"i": i}, "gold": [x], "steel": [k for k in range(n) if a[k] == k and k != x],
                          "eq": [f"{x} → seat {x}", "swap"], "caption": cap})
        else:
            why = [f"{x} ≥ {n} →", "no seat"] if x >= n else [f"{x} is home →", "next"]
            steps.append({"ptr": {"i": i}, "steel": [k for k in range(n) if a[k] == k], "gold": [i] if x >= n else [],
                          "eq": why, "caption": f"{x} has no seat, so move on." if x >= n else cap, "quick": x < n})
            i += 1
    m = next((k for k in range(n) if a[k] != k), n)
    steps.append({"ptr": {"i": m}, "steel": [k for k in range(n) if a[k] == k], "gold": [m], "eq": [f"seat {m} holds", f"{a[m]}, not {m}"],
                  "caption": "Scan: the seat with the wrong number."})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(15)
    cases = ["3 0 4 1 5", "3 0 1", "0 1", "9 6 4 2 3 5 7 0 1", "0", "1", "1 2 0", "2 0"]
    for _ in range(1300):
        n = _r.randint(1, 15)
        a = list(range(n + 1))
        a.remove(_r.randint(0, n))
        _r.shuffle(a)
        cases.append(" ".join(map(str, a)))
    a = list(range(5001)); a.remove(1234); _r.shuffle(a)
    cases.append(" ".join(map(str, a)))
    return cases


def expected(line):
    a = set(int(x) for x in line.split())
    return str(next(k for k in range(len(a) + 1) if k not in a))
