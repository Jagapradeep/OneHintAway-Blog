class Solution:
    # O(n) time, O(1) extra space
    def nextPermutation(self, nums: list[int]) -> None:
        n = len(nums)
        i = n - 2
        while i >= 0 and nums[i] >= nums[i + 1]:
            i = i - 1                # walk left
        if i >= 0:                   # pivot found
            j = n - 1
            while nums[j] <= nums[i]:
                j = j - 1
            nums[i], nums[j] = nums[j], nums[i]
        nums[i + 1:] = reversed(nums[i + 1:])
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    a = [int(x) for x in line.split()]
    Solution().nextPermutation(a)
    print(" ".join(map(str, a)))
