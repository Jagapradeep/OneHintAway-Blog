def bubble_sort(nums):
    n = len(nums)
    for sweep in range(1, n):
        swapped = False
        for j in range(0, n - sweep):
            if nums[j] > nums[j + 1]:
                nums[j], nums[j + 1] = nums[j + 1], nums[j]
                swapped = True
        if not swapped:
            return nums  # already sorted
    return nums
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    print(" ".join(map(str, bubble_sort([int(x) for x in line.split()]))))
