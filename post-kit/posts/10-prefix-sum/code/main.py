# build: O(n) time, O(n) space
def build_prefix(nums):
    n = len(nums)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + nums[i]
    return prefix

# query: O(1)
def range_sum(prefix, left, right):
    return prefix[right + 1] - prefix[left]
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    a, q = line.split("|")
    p = build_prefix([int(x) for x in a.split()])
    print(" ".join(str(range_sum(p, *map(int, pair.split()))) for pair in q.split(",")))
