# Reference for post 11 (LeetCode 560). Every number on the slides and in the video comes from here.

def subarray_sum(nums, k):
    seen = {0: 1}  # sum -> times seen; 0 is the empty start
    sum_ = 0
    count = 0
    for x in nums:
        sum_ = sum_ + x
        count = count + seen.get(sum_ - k, 0)
        seen[sum_] = seen.get(sum_, 0) + 1
    return count


def wrong_subarray_sum(nums, k):
    """The trap: no seen[0] = 1, so subarrays that start at index 0 are missed."""
    seen, s, count = {}, 0, 0
    for x in nums:
        s += x
        count += seen.get(s - k, 0)
        seen[s] = seen.get(s, 0) + 1
    return count


def running(nums):
    out, s = [0], 0
    for x in nums:
        s += x
        out.append(s)
    return out


EXAMPLE = [1, -1, 3, 1, 2]
K = 3
COUNT = subarray_sum(EXAMPLE, K)
SUMS = running(EXAMPLE)
WRONG = wrong_subarray_sum(EXAMPLE, K)


def video_steps(nums=EXAMPLE, k=K):
    seen, s, count = {0: 1}, 0, 0
    steps = [{"eq": ["seen:", "{0: 1}"], "caption": "Start with sum 0 seen once: the empty start."}]
    for i, x in enumerate(nums):
        s += x
        add = seen.get(s - k, 0)
        cap = f"Sum is {s}. Earlier sums of {s - k}: {add}."
        steps.append({"frame": [0, i], "gold": [i], "eq": [f"sum = {s}, need", f"{s - k}"], "caption": cap})
        count += add
        seen[s] = seen.get(s, 0) + 1
        steps.append({"frame": [0, i], "eq": ["count =", str(count)], "chip": f"+{add}", "chip_hl": add > 0, "caption": cap, "quick": True})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(11)
    cases = ["3 | 1 -1 3 1 2", "4 | 1 -1 3 1 2", "2 | 1 1 1", "3 | 1 2 3", "0 | 0 0 0", "0 | 1 -1 1 -1", "-5 | -5", "7 | 1"]
    for _ in range(1300):
        n = _r.randint(1, 14)
        a = [_r.randint(-5, 5) for _ in range(n)]
        cases.append(f"{_r.randint(-8, 8)} | " + " ".join(map(str, a)))
    big = [_r.randint(-1000, 1000) for _ in range(2000)]
    cases.append("500 | " + " ".join(map(str, big)))
    return cases


def expected(line):
    k, rest = line.split("|")
    k, a = int(k), [int(x) for x in rest.split()]
    c = 0
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]
            c += s == k
    return str(c)
