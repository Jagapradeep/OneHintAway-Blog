class Solution:
    # O(n) time, O(1) space: one pass, in place
    def sortColors(self, nums: list[int]) -> None:
        low = 0                   # next 0 goes here
        mid = 0                   # number to check
        high = len(nums) - 1      # next 2 goes here
        while mid <= high:
            if nums[mid] == 0:
                nums[low], nums[mid] = nums[mid], nums[low]
                low = low + 1
                mid = mid + 1
            elif nums[mid] == 1:
                mid = mid + 1
            else:
                nums[mid], nums[high] = nums[high], nums[mid]
                high = high - 1   # mid stays
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    a = [int(x) for x in line.split()]
    Solution().sortColors(a)
    print(" ".join(map(str, a)))
