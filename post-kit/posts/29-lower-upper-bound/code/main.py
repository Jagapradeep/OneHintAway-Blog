def lower_bound(nums, target):
    """First index whose value is >= target."""
    low = 0
    high = len(nums)  # one past the end
    while low < high:
        middle = (low + high) // 2
        if nums[middle] < target:
            low = middle + 1
        else:
            high = middle  # could be the answer
    return low
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    t, rest = line.split("|")
    a, t = [int(x) for x in rest.split()], int(t)
    print(lower_bound(a, t), lower_bound(a, t + 1))
