# Reference for post 18 (LeetCode 42). Every number on the slides and in the video comes from here.

def trap(height):
    left = 0
    right = len(height) - 1
    left_max = 0                # tallest wall seen
    right_max = 0
    water = 0
    while left < right:
        if height[left] < height[right]:
            bar = height[left]
            left_max = max(left_max, bar)
            water = water + left_max - bar
            left = left + 1
        else:
            bar = height[right]
            right_max = max(right_max, bar)
            water = water + right_max - bar
            right = right - 1
    return water


def wrong_trap(height):
    """The trap: settle the taller side instead of the lower one."""
    left, right, lm, rm, water = 0, len(height) - 1, 0, 0, 0
    while left < right:
        if height[left] > height[right]:
            lm = max(lm, height[left]); water += lm - height[left]; left += 1
        else:
            rm = max(rm, height[right]); water += rm - height[right]; right -= 1
    return water


def per_bar(height):
    return [max(0, min(max(height[:i + 1]), max(height[i:])) - h) for i, h in enumerate(height)]


EXAMPLE = [3, 0, 1, 4, 0, 2]
WATER = trap(EXAMPLE)
LEVELS = per_bar(EXAMPLE)
WRONG = wrong_trap(EXAMPLE)


def video_steps(h=EXAMPLE):
    left, right, lm, rm, total = 0, len(h) - 1, 0, 0, 0
    water = {}
    steps = [{"ptr": {"left": left, "right": right}, "eq": ["water =", "0"], "caption": "Settle the lower side first."}]
    while left < right:
        side = "left" if h[left] < h[right] else "right"
        steps.append({"ptr": {"left": left, "right": right}, "steel": [left, right], "water": dict(water),
                      "eq": [f"{h[left]} vs {h[right]} →", f"settle {side}"], "caption": "Compare the two ends. Settle the lower.", "quick": True})
        if h[left] < h[right]:
            bar = h[left]; lm = max(lm, bar); add = lm - bar; total += add
            if add:
                water[str(left)] = add
            cap = f"Left is lower: its wall is {lm}."
            steps.append({"ptr": {"left": left, "right": right}, "gold": [left], "water": dict(water),
                          "eq": [f"{lm} − {bar} =", f"+{add}"], "caption": cap})
            left += 1
        else:
            bar = h[right]; rm = max(rm, bar); add = rm - bar; total += add
            if add:
                water[str(right)] = add
            cap = f"Right is lower: its wall is {rm}."
            steps.append({"ptr": {"left": left, "right": right}, "gold": [right], "water": dict(water),
                          "eq": [f"{rm} − {bar} =", f"+{add}"], "caption": cap})
            right -= 1
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(18)
    cases = ["3 0 1 4 0 2", "0 1 0 2 1 0 1 3 2 1 2 1", "4 2 0 3 2 5", "2 0 2", "1", "1 2", "5 4 3 2 1", "1 2 3 4 5", "3 3 3", "0 0 0", "100000 0 100000"]
    for _ in range(1300):
        cases.append(" ".join(str(_r.randint(0, 6)) for _ in range(_r.randint(1, 14))))
    cases.append(" ".join(str(_r.randint(0, 10**5)) for _ in range(3000)))
    return cases


def expected(line):
    h = [int(x) for x in line.split()]
    n = len(h)
    lw, rw = h[:], h[:]
    for i in range(1, n):
        lw[i] = max(lw[i - 1], h[i])           # tallest wall up to i
    for i in range(n - 2, -1, -1):
        rw[i] = max(rw[i + 1], h[i])           # tallest wall from i
    return str(sum(min(lw[i], rw[i]) - h[i] for i in range(n)))
