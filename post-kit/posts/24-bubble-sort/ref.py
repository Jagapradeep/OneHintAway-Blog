# Reference for post 24. Every number on the slides and in the video comes from here.

def bubble_sort(nums):
    nums = list(nums)
    n = len(nums)
    for sweep in range(1, n):
        swapped = False
        for j in range(0, n - sweep):
            if nums[j] > nums[j + 1]:
                nums[j], nums[j + 1] = nums[j + 1], nums[j]
                swapped = True
        if not swapped:
            return nums
    return nums


def sweeps(nums):
    """How many sweeps run before the sort stops."""
    nums, n, count = list(nums), len(nums), 0
    for sweep in range(1, n):
        count += 1
        swapped = False
        for j in range(0, n - sweep):
            if nums[j] > nums[j + 1]:
                nums[j], nums[j + 1] = nums[j + 1], nums[j]
                swapped = True
        if not swapped:
            break
    return count


def swaps(nums):
    nums, n, total = list(nums), len(nums), 0
    for sweep in range(1, n):
        for j in range(0, n - sweep):
            if nums[j] > nums[j + 1]:
                nums[j], nums[j + 1] = nums[j + 1], nums[j]
                total += 1
    return total


def wrong_sort(nums):
    """The trap: the 'already sorted?' check sits inside the inner loop."""
    nums = list(nums)
    n = len(nums)
    for sweep in range(1, n):
        swapped = False
        for j in range(0, n - sweep):
            if nums[j] > nums[j + 1]:
                nums[j], nums[j + 1] = nums[j + 1], nums[j]
                swapped = True
            if not swapped:
                return nums
    return nums


def plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


EXAMPLE = [5, 2, 4, 1, 3]
SWEEPS = sweeps(EXAMPLE)
SWAPS = swaps(EXAMPLE)


def video_steps(nums=EXAMPLE):
    """Every comparison is a step: the pair is framed, it swaps or stays; each sweep ends with its count."""
    a = list(nums)
    n = len(a)
    steps = [{"eq": ["swaps so far:", "0"], "caption": "Walk the row and compare each pair of neighbours."}]
    total = 0
    for sweep in range(1, n):
        in_sweep = 0
        band = {"band": [n - sweep + 1, n - 1, "IN PLACE"]} if sweep > 1 else {}
        cap = f"Sweep {sweep}: compare each pair of neighbours."
        for j in range(0, n - sweep):
            x, y = a[j], a[j + 1]
            st = dict(band, frame=[j, j + 1], gold=[j + 1], caption=cap, hold=0.5)
            if x > y:
                a[j], a[j + 1] = y, x
                in_sweep += 1
                total += 1
                st.update(swap=[j, j + 1], eq=[f"{x} > {y} →", "swap"])
            else:
                st["eq"] = [f"{x} {'<' if x < y else '='} {y} →", "stay"]
            steps.append(st)
        steps.append({"band": [n - sweep, n - 1, "IN PLACE"], "eq": ["swaps so far:", str(total)],
                      "chip": f"sweep {sweep}: {in_sweep}", "chip_hl": in_sweep > 0,
                      "caption": f"Sweep {sweep} done: the {a[n - sweep]} is in place." if in_sweep
                      else f"Sweep {sweep}: no swaps at all."})
        if not in_sweep:
            break
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(24)
    cases = ["", "7", "2 1", "4 4 4", "1 2 3 4 5", "5 4 3 2 1", "2147483647 -2147483648 0", "5 2 4 1 3", "1 2 3 5 4"]
    cases.append(" ".join(str(_r.randint(-10**9, 10**9)) for _ in range(1000)))
    for _ in range(1201):
        cases.append(" ".join(str(_r.randint(-20, 20)) for _ in range(_r.randint(0, 12))))
    return cases


def expected(line):
    return " ".join(map(str, sorted(int(x) for x in line.split())))


TURTLE = [2, 3, 4, 5, 1]   # small value at the end: one step left per sweep
HARE = [5, 1, 2, 3, 4]     # big value at the front: to the end in one sweep
