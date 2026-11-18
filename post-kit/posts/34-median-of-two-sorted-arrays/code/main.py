def edge(nums, k, empty):
    if k < 0 or k >= len(nums):
        return empty
    return nums[k]


def median(a, b):
    if len(a) > len(b):
        return median(b, a)  # a: shorter
    m = len(a)
    n = len(b)
    half = (m + n + 1) // 2
    low = 0
    high = m
    while low < high:
        i = (low + high) // 2
        if b[half - i - 1] > a[i]:
            low = i + 1  # more from a
        else:
            high = i
    j = half - low  # low = the cut in a
    left_a = edge(a, low - 1, float("-inf"))
    left_b = edge(b, j - 1, float("-inf"))
    left_max = max(left_a, left_b)
    if (m + n) % 2 == 1:
        return left_max
    right_a = edge(a, low, float("inf"))
    right_b = edge(b, j, float("inf"))
    right_min = min(right_a, right_b)
    return (left_max + right_min) / 2
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    x, y = line.split("|")
    print(f"{float(median([int(v) for v in x.split()], [int(v) for v in y.split()])):.1f}")
