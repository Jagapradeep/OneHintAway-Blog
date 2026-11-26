# Reference for post 07 (GeeksforGeeks Max Sum Subarray of size K, LeetCode 643's core).

def max_sum(nums, k):
    total = 0
    for i in range(k):
        total = total + nums[i]
    best = total
    for i in range(k, len(nums)):
        total = total + nums[i] - nums[i - k]
        best = max(best, total)
    return best


def wrong_max_sum(nums, k):
    """The trap: subtract nums[i - k + 1], a number that is still inside the window."""
    total = sum(nums[:k])
    best = total
    for i in range(k, len(nums)):
        total = total + nums[i] - nums[i - k + 1]
        best = max(best, total)
    return best


def window_sums(nums, k):
    return [sum(nums[i:i + k]) for i in range(len(nums) - k + 1)]


def wrong_sums(nums, k):
    total, out = sum(nums[:k]), [sum(nums[:k])]
    for i in range(k, len(nums)):
        total = total + nums[i] - nums[i - k + 1]
        out.append(total)
    return out


EXAMPLE = [2, 1, 5, 1, 3, 2]
K = 3
BEST = max_sum(EXAMPLE, K)
SUMS = window_sums(EXAMPLE, K)
BEST_AT = SUMS.index(BEST)


def video_steps(nums=EXAMPLE, k=K):
    steps = [{"eq": ["k =", str(k)], "caption": f"Add up the first {k} numbers."}]
    total = 0
    for i in range(k):
        total += nums[i]
        steps.append({"frame": [0, i], "gold": [i], "eq": ["total =", str(total)], "caption": f"Add up the first {k} numbers.", "quick": True})
    best = total
    steps.append({"frame": [0, k - 1], "eq": ["best =", str(best)], "chip": f"{total}", "caption": f"Add up the first {k} numbers."})
    for i in range(k, len(nums)):
        old = total
        total = total + nums[i] - nums[i - k]
        cap = f"One in, one out: + {nums[i]}, − {nums[i - k]}."
        steps.append({"frame": [i - k + 1, i], "gold": [i], "dim": [i - k], "eq": [f"{old} + {nums[i]} − {nums[i - k]} =", str(total)],
                      "caption": cap})
        best = max(best, total)
        steps.append({"frame": [i - k + 1, i], "eq": ["best =", str(best)], "chip": str(total), "chip_hl": total == best and total > old,
                      "caption": cap, "quick": True})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(7)
    cases = ["3 | 2 1 5 1 3 2", "1 | 5", "1 | -3 -1 -2", "2 | 4 2 7 1", "4 | 1 12 -5 -6 50 3", "5 | 1 1 1 1 1",
             "2 | -10000 -10000", "3 | 10000 10000 10000 10000"]
    for _ in range(1300):
        n = _r.randint(1, 14)
        a = [_r.randint(-20, 20) for _ in range(n)]
        cases.append(f"{_r.randint(1, n)} | " + " ".join(map(str, a)))
    big = [_r.randint(-10**4, 10**4) for _ in range(5000)]
    cases.append("700 | " + " ".join(map(str, big)))
    return cases


def expected(line):
    k, rest = line.split("|")
    k, a = int(k), [int(x) for x in rest.split()]
    return str(max(sum(a[i:i + k]) for i in range(len(a) - k + 1)))
