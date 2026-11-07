def search(nums, target):
    low = 0
    high = len(nums) - 1
    while low <= high:
        middle = low + (high - low) // 2
        if nums[middle] == target:
            return middle
        elif nums[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    t, rest = line.split("|")
    print(search([int(x) for x in rest.split()], int(t)))
