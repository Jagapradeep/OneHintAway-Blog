import math


def pumps_needed(stations, d):
    count = 0
    for i in range(1, len(stations)):
        gap = stations[i] - stations[i - 1]
        count += math.ceil(gap / d) - 1
    return count


def min_max_gap(stations, k):
    n = len(stations)
    low = 0.0
    high = float(stations[n - 1] - stations[0])
    while high - low > 0.000001:
        d = (low + high) / 2
        if pumps_needed(stations, d) <= k:
            high = d  # fits: go lower
        else:
            low = d  # too many: go higher
    return high
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    k, rest = line.split("|")
    print(f"{min_max_gap([int(x) for x in rest.split()], int(k)):.2f}")
