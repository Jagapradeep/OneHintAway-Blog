def partition(nums, low, high):
    pivot = nums[high]
    wall = low  # next slot for a small value
    for j in range(low, high):
        if nums[j] < pivot:
            nums[wall], nums[j] = nums[j], nums[wall]
            wall += 1
    nums[wall], nums[high] = nums[high], nums[wall]
    return wall


def quick_sort(nums, low, high):
    if low < high:
        spot = partition(nums, low, high)
        quick_sort(nums, low, spot - 1)
        quick_sort(nums, spot + 1, high)


def quick_select(nums, k):  # k-th smallest, k from 1
    low = 0
    high = len(nums) - 1
    while True:
        spot = partition(nums, low, high)
        if spot == k - 1:
            return nums[spot]
        if spot < k - 1:
            low = spot + 1  # answer is right
        else:
            high = spot - 1  # answer is left
# ---- test harness: not on the blog ----
import sys
sys.setrecursionlimit(10000)
for line in sys.stdin.read().split("\n")[:-1]:
    k, rest = line.split("|")
    a = [int(x) for x in rest.split()]
    b = a[:]
    quick_sort(a, 0, len(a) - 1)
    print(" ".join(map(str, a)) + "|" + str(quick_select(b, int(k))))
