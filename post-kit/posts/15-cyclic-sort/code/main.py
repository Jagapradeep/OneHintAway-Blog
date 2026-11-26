class Solution:
    # O(n) time, O(1) extra space
    def missingNumber(self, nums: list[int]) -> int:
        n = len(nums)
        i = 0
        while i < n:
            seat = nums[i]
            if seat < n and nums[seat] != seat:
                nums[i], nums[seat] = nums[seat], nums[i]
            else:
                i = i + 1          # home, or no seat
        for i in range(n):
            if nums[i] != i:       # wrong number
                return i
        return n
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    print(Solution().missingNumber([int(x) for x in line.split()]))
