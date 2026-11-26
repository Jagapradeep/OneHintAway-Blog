# Reference for post 08: the longest run of days within a budget (every number positive).

def longest_within(nums, budget):
    left = 0
    total = 0
    best = 0
    for right in range(len(nums)):
        total = total + nums[right]
        while total > budget:
            total = total - nums[left]
            left = left + 1
        best = max(best, right - left + 1)
    return best


def wrong_longest(nums, budget):
    """The trap: measure first, then shrink, so a window over budget is counted."""
    left = total = best = 0
    for right in range(len(nums)):
        total += nums[right]
        best = max(best, right - left + 1)
        while total > budget:
            total -= nums[left]
            left += 1
    return best


EXAMPLE = [2, 1, 3, 1, 4]
BUDGET = 5
BEST = longest_within(EXAMPLE, BUDGET)
MOVES = 2 * len(EXAMPLE)


def video_steps(nums=EXAMPLE, budget=BUDGET):
    steps = [{"eq": ["budget =", str(budget)], "caption": "Grow on the right, shrink on the left."}]
    left = total = best = 0
    for right in range(len(nums)):
        total += nums[right]
        over = total > budget
        cap = f"{nums[right]} joins. Over {budget}? Drop from the left." if over else f"{nums[right]} joins, and the total still fits."
        steps.append({"frame": [left, right], "ptr": {"left": left, "right": right}, "gold": [right],
                      "eq": ["total =", f"{total}" + (f" > {budget}" if over else "")], "caption": cap})
        while total > budget:
            total -= nums[left]
            steps.append({"frame": [left + 1, right], "ptr": {"left": left + 1, "right": right}, "dim": list(range(left + 1)),
                          "eq": [f"drop {nums[left]} →", f"total {total}"], "caption": cap, "hold": 0.6})
            left += 1
        best = max(best, right - left + 1)
        steps.append({"frame": [left, right], "ptr": {"left": left, "right": right}, "dim": list(range(left)),
                      "eq": ["length =", str(right - left + 1)],
                      "caption": cap, "quick": True})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(8)
    cases = ["5 | 2 1 3 1 4", "4 | 1 1 1 3 1", "0 | 1 2 3", "100 | 1 2 3", "1 | 1", "3 | 4", "7 | 7 7 7",
             "1000000000 | 1000000000 1000000000 1", "6 | 1 2 3 4 5"]
    for _ in range(1300):
        n = _r.randint(1, 14)
        a = [_r.randint(1, 10) for _ in range(n)]
        cases.append(f"{_r.randint(0, 30)} | " + " ".join(map(str, a)))
    big = [_r.randint(1, 10**4) for _ in range(3000)]
    cases.append("500000 | " + " ".join(map(str, big)))
    return cases


def expected(line):
    b, rest = line.split("|")
    b, a = int(b), [int(x) for x in rest.split()]
    best = 0
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]
            if s > b:
                break
            best = max(best, j - i + 1)
    return str(best)
