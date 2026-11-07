def merge_sort(nums):
    if len(nums) <= 1:
        return nums
    middle = len(nums) // 2
    left = merge_sort(nums[:middle])
    right = merge_sort(nums[middle:])
    return merge(left, right)


def merge(left, right):
    result = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    return result + left[i:] + right[j:]
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    print(" ".join(map(str, merge_sort([int(x) for x in line.split()]))))
