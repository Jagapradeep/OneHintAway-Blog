def insertion_sort(nums):
    for i in range(1, len(nums)):
        card = nums[i]
        j = i - 1
        while j >= 0 and nums[j] > card:
            nums[j + 1] = nums[j]
            j -= 1
        nums[j + 1] = card
    return nums
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    print(" ".join(map(str, insertion_sort([int(x) for x in line.split()]))))
