def find_min(nums):
    low = 0
    high = len(nums) - 1
    while low < high:
        middle = (low + high) // 2
        if nums[middle] > nums[high]:
            low = middle + 1  # the drop is to the right
        else:
            high = middle  # middle may be the minimum
    return nums[low]
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    print(find_min([int(x) for x in line.split()]))
