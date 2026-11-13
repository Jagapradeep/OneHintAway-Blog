# Reference for post 26. Every number on the slides and in the video comes from here.

def partition(nums, low, high):
    pivot = nums[high]
    wall = low
    for j in range(low, high):
        if nums[j] < pivot:
            nums[wall], nums[j] = nums[j], nums[wall]
            wall = wall + 1
    nums[wall], nums[high] = nums[high], nums[wall]
    return wall


def quick_sort(nums, low=None, high=None, _top=True):
    if _top:
        nums = list(nums)
        low, high = 0, len(nums) - 1
    if low < high:
        spot = partition(nums, low, high)
        quick_sort(nums, low, spot - 1, False)
        quick_sort(nums, spot + 1, high, False)
    return nums


def quick_select(nums, k):
    """k-th smallest, k from 1."""
    nums = list(nums)
    low, high = 0, len(nums) - 1
    while True:
        spot = partition(nums, low, high)
        if spot == k - 1:
            return nums[spot]
        if spot < k - 1:
            low = spot + 1
        else:
            high = spot - 1


def kth_largest(nums, k):
    return quick_select(nums, len(nums) - k + 1)


def wrong_kth_largest(nums, k):
    """The trap: pass k straight in. quickSelect counts from the smallest."""
    return quick_select(nums, k)


def partitioned(nums):
    a = list(nums)
    spot = partition(a, 0, len(a) - 1)
    return a, spot


def spot_of(nums):
    return partitioned(nums)[1]


def select_rounds(nums, k):
    nums = list(nums)
    low, high, rounds = 0, len(nums) - 1, 0
    while True:
        rounds += 1
        spot = partition(nums, low, high)
        if spot == k - 1:
            return rounds
        if spot < k - 1:
            low = spot + 1
        else:
            high = spot - 1


EXAMPLE = [5, 2, 4, 1, 3]
AFTER, SPOT = partitioned(EXAMPLE)


def video_steps(nums=EXAMPLE):
    a = list(nums)
    steps = []
    placed = []

    def sp(x):
        return " ".join(map(str, x))

    def go(low, high):
        if low > high:
            return
        if low == high:
            placed.append(low)
            return
        pivot = a[high]
        steps.append({"frame": [low, high], "gold": [high], "steel": list(placed), "eq": ["pivot =", str(pivot)],
                      "caption": f"Pivot {pivot}: smaller values go left of it." if low == 0 and high == len(a) - 1 else f"Same move on {sp(a[low:high + 1])}: pivot {pivot}."})
        wall = low
        cap = steps[-1]["caption"]
        for j in range(low, high):          # one step per value checked against the pivot
            st = {"frame": [low, high], "gold": [high], "steel": list(placed), "ptr": {"wall": wall, "j": j},
                  "caption": cap, "hold": 0.6}
            if a[j] < pivot:
                st["eq"] = [f"{a[j]} < {pivot} →", f"slot {wall}"]
                if wall != j:
                    st["swap"] = [wall, j]
                a[wall], a[j] = a[j], a[wall]
                wall += 1
            else:
                st["eq"] = [f"{a[j]} {'>' if a[j] > pivot else '='} {pivot} →", "stays"]
            steps.append(st)
        moved = wall != high
        a[wall], a[high] = a[high], a[wall]
        placed.append(wall)
        st = {"frame": [low, high], "gold": [wall], "steel": [p for p in placed if p != wall],
              "eq": [f"{pivot} lands at", f"slot {wall}"], "chip": f"{pivot} → slot {wall}", "chip_hl": True,
              "caption": f"The {pivot} swaps into slot {wall}. It never moves again."}
        if moved:
            st["swap"] = [wall, high]
        steps.append(st)
        go(low, wall - 1)
        go(wall + 1, high)
    go(0, len(a) - 1)
    for s in steps:
        if not s.get("steel"):
            s.pop("steel", None)
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(26)
    cases = ["1|7", "1|2 1", "2|2 1", "2|4 4 4", "3|1 2 3 4 5", "1|5 4 3 2 1", "2|2147483647 -2147483648 0",
             "3|5 2 4 1 3", "4|5 2 4 1 3", "2|3 1 3 1 2"]
    big = [_r.randint(-10**9, 10**9) for _ in range(1000)]
    cases.append(f"{_r.randint(1, 1000)}|" + " ".join(map(str, big)))
    for _ in range(1200):
        n = _r.randint(1, 12)
        cases.append(f"{_r.randint(1, n)}|" + " ".join(str(_r.randint(-20, 20)) for _ in range(n)))
    return cases


def expected(line):
    k, rest = line.split("|")
    a = sorted(int(x) for x in rest.split())
    return " ".join(map(str, a)) + "|" + str(a[int(k) - 1])
