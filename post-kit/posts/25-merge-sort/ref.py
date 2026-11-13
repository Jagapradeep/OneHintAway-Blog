# Reference for post 25. Every number on the slides and in the video comes from here.

def merge(left, right):
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i = i + 1
        else:
            result.append(right[j])
            j = j + 1
    return result + left[i:] + right[j:]


def merge_sort(nums):
    if len(nums) <= 1:
        return list(nums)
    middle = len(nums) // 2
    left = merge_sort(nums[:middle])
    right = merge_sort(nums[middle:])
    return merge(left, right)


def merge_compares(left, right):
    i = j = c = 0
    while i < len(left) and j < len(right):
        c += 1
        if left[i] <= right[j]:
            i += 1
        else:
            j += 1
    return c


def wrong_merge(left, right):
    """The trap: forget the leftovers."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result


def wrong_sort(nums):
    if len(nums) <= 1:
        return list(nums)
    middle = len(nums) // 2
    return wrong_merge(wrong_sort(nums[:middle]), wrong_sort(nums[middle:]))


EXAMPLE = [5, 2, 4, 6, 1, 3]
LEFT_SORTED = merge_sort(EXAMPLE[:3])
RIGHT_SORTED = merge_sort(EXAMPLE[3:])


def merge_events(nums=EXAMPLE):
    a = list(nums)
    events = []

    def go(lo, hi):          # sorts a[lo..hi] inclusive
        if hi - lo + 1 <= 1:
            return
        mid = lo + (hi - lo + 1) // 2
        go(lo, mid - 1)
        go(mid, hi)
        left, right = a[lo:mid], a[mid:hi + 1]
        merged = merge(left, right)
        a[lo:hi + 1] = merged
        events.append((lo, hi, left, right, merged))
    go(0, len(a) - 1)
    return events


MERGES = len(merge_events())
LEVELS = 3


def video_steps(nums=EXAMPLE):
    n = len(nums)
    half = (n - 1) // 2
    cuts = set(range(n - 1))
    steps = [{"eq": ["pieces:", "1"], "caption": "One unsorted array of 6 values."},
             {"cuts": [half], "eq": ["pieces:", "2"], "caption": "Split it into two halves."},
             {"cuts": sorted(cuts), "eq": ["pieces:", str(n)], "caption": "Keep splitting. One value is sorted."}]
    for k, (lo, hi, left, right, merged) in enumerate(merge_events(nums), 1):
        sp = lambda x: " ".join(map(str, x))
        cuts -= set(range(lo, hi))
        eq_left = f"{sp(left)} + {sp(right)} →"
        cap = f"Merge {sp(left)} with {sp(right)}."
        # the two pieces close up first, then their cards glide into order
        steps.append({"frame": [lo, hi], "cuts": sorted(cuts), "eq": [eq_left, ""], "caption": cap, "quick": True})
        steps.append({"frame": [lo, hi], "sort": [lo, hi], "cuts": sorted(cuts), "eq": [eq_left, sp(merged)],
                      "chip": f"size {hi - lo + 1}", "chip_hl": hi - lo + 1 == len(nums), "caption": cap})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(25)
    cases = ["", "7", "2 1", "4 4 4", "1 2 3 4 5", "5 4 3 2 1", "2147483647 -2147483648 0", "5 2 4 6 1 3", "3 1 3 1 2"]
    cases.append(" ".join(str(_r.randint(-10**9, 10**9)) for _ in range(1000)))
    for _ in range(1201):
        cases.append(" ".join(str(_r.randint(-20, 20)) for _ in range(_r.randint(0, 13))))
    return cases


def expected(line):
    return " ".join(map(str, sorted(int(x) for x in line.split())))
