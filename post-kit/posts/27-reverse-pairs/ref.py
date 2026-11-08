# Reference for post 27 (LeetCode 493). Every number on the slides and in the video comes from here.

def reverse_pairs(nums):
    a = list(nums)
    events = []

    def count_pairs(low, high):
        if low >= high:
            return 0
        mid = (low + high) // 2
        left = count_pairs(low, mid)
        right = count_pairs(mid + 1, high)
        count = left + right
        i = low
        across = 0
        for j in range(mid + 1, high + 1):
            twice = 2 * a[j]
            while i <= mid and a[i] <= twice:
                i += 1
            across += mid - i + 1
        count += across
        before_l, before_r = a[low:mid + 1], a[mid + 1:high + 1]
        a[low:high + 1] = sorted(a[low:high + 1])      # the merge (post 25)
        events.append((low, high, before_l, before_r, across))
        return count

    total = count_pairs(0, len(a) - 1)
    reverse_pairs.events = events
    return total


def brute(nums):
    n = len(nums)
    return sum(1 for i in range(n) for j in range(i + 1, n) if nums[i] > 2 * nums[j])


def pairs(nums):
    n = len(nums)
    return [(nums[i], nums[j]) for i in range(n) for j in range(i + 1, n) if nums[i] > 2 * nums[j]]


def cross(left, right):
    """Pairs across two sorted halves, by the walk."""
    i, c = 0, 0
    for r in right:
        while i < len(left) and left[i] <= 2 * r:
            i += 1
        c += len(left) - i
    return c


EXAMPLE = [6, 4, 1, 5, 2]
TOTAL = reverse_pairs(EXAMPLE)
PAIRS = ", ".join(f"({x}, {y})" for x, y in pairs(EXAMPLE))
ALL_PAIRS = len(EXAMPLE) * (len(EXAMPLE) - 1) // 2
LEFT_HALF = sorted(EXAMPLE[:3])
RIGHT_HALF = sorted(EXAMPLE[3:])


def video_steps(nums=EXAMPLE):
    reverse_pairs(nums)
    n = len(nums)
    sp = lambda x: " ".join(map(str, x))
    cuts = set(range(n - 1))
    steps = [{"eq": ["pairs =", "0"], "caption": "Split until each piece is one value."},
             {"cuts": sorted(cuts), "eq": ["pairs =", "0"], "caption": "Now count and merge on the way up."}]
    total = 0
    for low, high, L, R, c in reverse_pairs.events:
        total += c
        merged = sorted(L + R)
        cuts -= set(range(low, high))
        steps.append({"frame": [low, high], "set": {str(low + t): v for t, v in enumerate(merged)}, "cuts": sorted(cuts),
                      "eq": [f"{sp(L)} | {sp(R)} → +{c}", f"{total}"], "chip": f"+{c}", "chip_hl": c > 0,
                      "caption": f"{c} pair{'s' if c != 1 else ''} across, then merge." if c else "No pair across, then merge."})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(27)
    M = 2**31 - 1
    cases = ["7", "2 1", "3 1", "1 3 2 3 1", "2 4 3 5 1", "6 4 1 5 2", "5 4 3 2 1", "1 2 3 4 5", "4 4 4 4",
             f"{M} {M} {M}", f"{M} -{M + 1}", f"-{M + 1} -{M + 1}", f"{M} 1073741823 1073741824",
             "-5 -3 -1", "0 0 0", "-1 -1 -1 -2"]
    cases.append(" ".join(str(_r.randint(-M - 1, M)) for _ in range(2000)))
    for _ in range(600):
        cases.append(" ".join(str(_r.randint(-20, 20)) for _ in range(_r.randint(1, 14))))
    for _ in range(400):
        cases.append(" ".join(str(_r.randint(-M - 1, M)) for _ in range(_r.randint(1, 30))))
    return cases


def expected(line):
    return str(brute([int(x) for x in line.split()]))
