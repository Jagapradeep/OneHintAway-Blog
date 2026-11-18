def build(nums, i, picked, out):
    if i == len(nums):
        out.append(list(picked))  # a copy
    else:
        picked.append(nums[i])  # pick
        build(nums, i + 1, picked, out)
        picked.pop()  # skip
        build(nums, i + 1, picked, out)


def subsets(nums):
    out = []
    build(nums, 0, [], out)
    return out
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    res = subsets([int(x) for x in line.split()])
    print(",".join(" ".join(map(str, s)) for s in res))
