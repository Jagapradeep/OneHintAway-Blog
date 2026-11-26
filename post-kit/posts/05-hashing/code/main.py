class Solution:
    # Hash map: O(n) time, O(n) space
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        seen = {}                      # value -> index
        for i in range(len(nums)):
            need = target - nums[i]
            if need in seen:
                return [seen[need], i]
            seen[nums[i]] = i
        return None
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    t, rest = line.split("|")
    r = Solution().twoSum([int(x) for x in rest.split()], int(t))
    print("none" if r is None else f"{r[0]} {r[1]}")
