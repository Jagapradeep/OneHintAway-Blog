class Solution:
    # O(n) time, O(1) space. Every number must be positive.
    def longestWithin(self, nums: list[int], budget: int) -> int:
        left = 0
        total = 0
        best = 0
        for right in range(len(nums)):
            total = total + nums[right]
            while total > budget:
                total = total - nums[left]
                left = left + 1
            best = max(best, right - left + 1)
        return best
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    b, rest = line.split("|")
    print(Solution().longestWithin([int(x) for x in rest.split()], int(b)))
