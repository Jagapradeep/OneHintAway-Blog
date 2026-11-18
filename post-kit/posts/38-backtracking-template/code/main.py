def permute(nums, used, path, out):
    if len(path) == len(nums):
        out.append(list(path))
        return out
    for i in range(len(nums)):
        if not used[i]:
            used[i] = True  # choose
            path.append(nums[i])
            permute(nums, used, path, out)
            path.pop()  # undo
            used[i] = False
    return out


def find(nums, i, left, path, out):
    if left == 0:
        out.append(list(path))
        return out
    for j in range(i, len(nums)):
        if nums[j] <= left:
            path.append(nums[j])  # choose
            rest = left - nums[j]
            find(nums, j, rest, path, out)
            path.pop()  # undo
    return out
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    p = line.split("|")
    if p[0] == "P":
        nums = [int(x) for x in p[1].split()]
        res = permute(nums, [False] * len(nums), [], [])
    else:
        res = find([int(x) for x in p[2].split()], 0, int(p[1]), [], [])
    print(",".join(" ".join(map(str, s)) for s in res))
