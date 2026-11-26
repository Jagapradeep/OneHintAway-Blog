class Solution:
    # O(n) time, O(1) space
    def maxSum(self, nums: list[int], k: int) -> int:
        total = 0
        for i in range(k):
            total = total + nums[i]
        best = total
        for i in range(k, len(nums)):
            total = total + nums[i] - nums[i - k]
            best = max(best, total)
        return best
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    k, rest = line.split("|")
    print(Solution().maxSum([int(x) for x in rest.split()], int(k)))
