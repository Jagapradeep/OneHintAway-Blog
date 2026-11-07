def reverse_pairs(nums):
    n = len(nums)
    return count_pairs(nums, 0, n - 1)


def count_pairs(nums, low, high):
    if low >= high:
        return 0
    mid = (low + high) // 2
    left = count_pairs(nums, low, mid)
    right = count_pairs(nums, mid + 1, high)
    count = left + right
    i = low
    for j in range(mid + 1, high + 1):
        twice = 2 * nums[j]
        while i <= mid and nums[i] <= twice:
            i += 1
        count += mid - i + 1
    merge(nums, low, mid, high)  # the merge from post 25
    return count


def merge(nums, low, mid, high):
    merged = []
    a, b = low, mid + 1
    while a <= mid and b <= high:
        if nums[a] <= nums[b]:
            merged.append(nums[a])
            a += 1
        else:
            merged.append(nums[b])
            b += 1
    merged += nums[a:mid + 1] + nums[b:high + 1]
    nums[low:high + 1] = merged
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    print(reverse_pairs([int(x) for x in line.split()]))
