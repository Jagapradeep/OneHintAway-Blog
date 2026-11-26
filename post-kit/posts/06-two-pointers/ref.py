# Reference for post 06 (LeetCode 167). Every number on the slides and in the video comes from here.

def two_sum(numbers, target):
    left = 0
    right = len(numbers) - 1
    while left < right:
        total = numbers[left] + numbers[right]
        if total == target:
            return [left + 1, right + 1]
        elif total < target:
            left = left + 1
        else:
            right = right - 1
    return None


def pair_values(numbers, target):
    r = two_sum(numbers, target)
    return None if r is None else [numbers[r[0] - 1], numbers[r[1] - 1]]


def checks(numbers, target):
    left, right, c = 0, len(numbers) - 1, 0
    while left < right:
        c += 1
        s = numbers[left] + numbers[right]
        if s == target:
            return c
        if s < target:
            left += 1
        else:
            right -= 1
    return c


EXAMPLE = [1, 3, 4, 6, 8, 11]
TARGET = 10
ANSWER = two_sum(EXAMPLE, TARGET)
CHECKS = checks(EXAMPLE, TARGET)
PAIRS = len(EXAMPLE) * (len(EXAMPLE) - 1) // 2
UNSORTED = [1, 4, 6, 3]
WRONG = two_sum(UNSORTED, 10)                       # None: the trap
RIGHT = pair_values(sorted(UNSORTED), 10)           # [4, 6]


def video_steps(nums=EXAMPLE, target=TARGET):
    left, right = 0, len(nums) - 1
    steps = [{"ptr": {"left": left, "right": right}, "eq": ["target =", str(target)],
              "caption": "Start at both ends of the sorted array."}]
    while left < right:
        s = nums[left] + nums[right]
        dim = [i for i in range(len(nums)) if i < left or i > right]
        base = {"ptr": {"left": left, "right": right}, "gold": [left, right]}
        if dim:
            base["dim"] = dim
        if s == target:
            steps.append(dict(base, eq=[f"{nums[left]} + {nums[right]} =", f"{s} found"], chip=f"{s} ✓", chip_hl=True,
                              caption=f"{nums[left]} + {nums[right]} is exactly {target}."))
            return steps
        if s > target:
            steps.append(dict(base, eq=[f"{nums[left]} + {nums[right]} = {s} →", "right in"], chip=f"{s} >",
                              caption=f"Too big, so {nums[right]} can't be in the pair."))
            right -= 1
        else:
            steps.append(dict(base, eq=[f"{nums[left]} + {nums[right]} = {s} →", "left in"], chip=f"{s} <",
                              caption=f"Too small, so {nums[left]} can't be in the pair."))
            left += 1
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def _pairs(a, t):
    return [(i, j) for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] + a[j] == t]


def test_inputs():
    _r.seed(6)
    cases = ["10 | 1 3 4 6 8 11", "9 | 2 7 11 15", "6 | 2 3 4", "-1 | -1 0", "2 | 1 1", "100 | 1 2 3 4",
             "2000000000 | 0 1000000000 1000000000", "-2000000000 | -1000000000 -1000000000 5"]
    while len(cases) < 1300:
        n = _r.randint(2, 12)
        a = sorted(_r.randint(-30, 30) for _ in range(n))
        if _r.random() < 0.2:
            t = _r.randint(-70, 70)
            if _pairs(a, t):
                continue
        else:
            i, j = sorted(_r.sample(range(n), 2))
            t = a[i] + a[j]
            if len(_pairs(a, t)) != 1:
                continue
        cases.append(f"{t} | " + " ".join(map(str, a)))
    big = sorted(_r.sample(range(-10**9, 10**9), 3000))
    t = big[17] + big[2950]
    if len(_pairs(big[:0] or big, t)) == 1:
        cases.append(f"{t} | " + " ".join(map(str, big)))
    return cases


def expected(line):
    t, rest = line.split("|")
    a = [int(x) for x in rest.split()]
    p = _pairs(a, int(t))
    return "none" if not p else f"{p[0][0] + 1} {p[0][1] + 1}"
