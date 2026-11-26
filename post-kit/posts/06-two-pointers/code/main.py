class Solution:
    # Two pointers: O(n) time, O(1) space
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        left = 0
        right = len(nums) - 1
        while left < right:
            total = nums[left] + nums[right]
            if total == target:
                return [left + 1, right + 1]
            elif total < target:
                left = left + 1
            else:
                right = right - 1
        return None
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    t, rest = line.split("|")
    r = Solution().twoSum([int(x) for x in rest.split()], int(t))
    print("none" if r is None else f"{r[0]} {r[1]}")
