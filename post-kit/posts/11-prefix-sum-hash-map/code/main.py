# O(n) time, O(n) space
def subarray_sum(nums, k):
    seen = {0: 1}  # sum -> times seen; 0 is the empty start
    sum = 0
    count = 0
    for x in nums:
        sum = sum + x
        count = count + seen.get(sum - k, 0)
        seen[sum] = seen.get(sum, 0) + 1
    return count
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    k, rest = line.split("|")
    print(subarray_sum([int(x) for x in rest.split()], int(k)))
