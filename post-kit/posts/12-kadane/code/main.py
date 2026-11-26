class Solution:
    # O(n) time, O(1) space
    def maxSubArray(self, nums: list[int]) -> int:
        current = 0          # sum so far
        best = nums[0]       # largest so far
        for x in nums:
            if current < 0:  # in debt?
                current = 0  # start fresh
            current = current + x
            best = max(best, current)
        return best
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    print(Solution().maxSubArray([int(x) for x in line.split()]))
