# Reference for post 18 (LeetCode 42). Every number on the slides and in the video comes from here.

def trap(height):
    left, right = 0, len(height) - 1
    left_max = right_max = water = 0
    while left < right:
        if height[left] < height[right]:
            bar = height[left]
            left_max = max(left_max, bar)
            water += left_max - bar
            left += 1
        else:
            bar = height[right]
            right_max = max(right_max, bar)
            water += right_max - bar
            right -= 1
    return water


def water_per_bar(height):
    return [max(0, min(max(height[:i + 1]), max(height[i:])) - h) for i, h in enumerate(height)]


EXAMPLE = [3, 0, 1, 4, 0, 2]
TOTAL = trap(EXAMPLE)
PER_BAR = water_per_bar(EXAMPLE)


def video_steps(height=EXAMPLE):
    left, right = 0, len(height) - 1
    lm = rm = total = 0
    water = {}
    steps = [{"ptr": {"left": left, "right": right}, "eq": ["water =", "0"], "caption": "Two walkers start at the two ends."}]
    while left < right:
        if height[left] < height[right]:
            i, bar = left, height[left]
            lm = max(lm, bar)
            w, best, side = lm - bar, lm, "leftMax"
            left += 1
        else:
            i, bar = right, height[right]
            rm = max(rm, bar)
            w, best, side = rm - bar, rm, "rightMax"
            right -= 1
        total += w
        if w:
            water[i] = w
        steps.append({"ptr": {"left": left, "right": right}, "gold": [i], "water": dict(water),
                      "eq": [f"{side} {best} − {bar} =", f"{w}"], "chip": f"+{w}", "chip_hl": w > 0,
                      "caption": (f"Bar {i} holds {w}." if w else f"Bar {i} holds nothing.") + " Its walker steps in."})
    return steps
