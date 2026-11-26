class Solution:
    # O(n) time, O(1) space. LeetCode 169 promises a majority.
    def majorityElement(self, nums: list[int]) -> int:
        candidate = None
        count = 0
        for x in nums:
            if count == 0:
                candidate = x   # new candidate
            if x == candidate:
                count = count + 1
            else:
                count = count - 1
        return candidate
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    print(Solution().majorityElement([int(x) for x in line.split()]))
