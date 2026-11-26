class Solution:
    # O(n) time, O(1) space
    def trap(self, height: list[int]) -> int:
        left = 0
        right = len(height) - 1
        leftMax = 0                # tallest wall seen
        rightMax = 0
        water = 0
        while left < right:
            if height[left] < height[right]:
                bar = height[left]
                leftMax = max(leftMax, bar)
                water = water + leftMax - bar
                left = left + 1
            else:
                bar = height[right]
                rightMax = max(rightMax, bar)
                water = water + rightMax - bar
                right = right - 1
        return water
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    print(Solution().trap([int(x) for x in line.split()]))
