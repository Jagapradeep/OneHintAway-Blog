# Reference for post 22. Every number on the slides and in the video comes from here.

def insertion_sort(nums):
    nums = list(nums)
    for i in range(1, len(nums)):
        card = nums[i]
        j = i - 1
        while j >= 0 and nums[j] > card:
            nums[j + 1] = nums[j]
            j = j - 1
        nums[j + 1] = card
    return nums


def shifts(nums):
    nums, total = list(nums), 0
    for i in range(1, len(nums)):
        card, j = nums[i], i - 1
        while j >= 0 and nums[j] > card:
            nums[j + 1] = nums[j]
            j -= 1
            total += 1
        nums[j + 1] = card
    return total


def wrong_sort(nums):
    """The trap: no saved card, uses nums[i] in lines 5 and 8."""
    nums = list(nums)
    for i in range(1, len(nums)):
        j = i - 1
        while j >= 0 and nums[j] > nums[i]:
            nums[j + 1] = nums[j]
            j = j - 1
        nums[j + 1] = nums[i]
    return nums


def plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")


EXAMPLE = [5, 2, 4, 1, 3]


def video_steps(nums=EXAMPLE):
    a = list(nums)
    steps = [{"band": [0, 0, "SORTED PART"], "eq": ["sorted:", str(a[0])], "caption": "One card on its own is already sorted."}]
    for i in range(1, len(a)):
        card, j = a[i], i - 1
        bigger = []
        while j >= 0 and a[j] > card:
            bigger.append(a[j])
            j -= 1
        a.insert(j + 1, a.pop(i))
        if bigger:
            eq = [", ".join(map(str, bigger)) + f" > {card} →", f"index {j + 1}"]
            cap = f"{card} slides left past {', '.join(map(str, bigger))}."
        else:
            eq = [f"{a[j]} < {card} →", "stays"]
            cap = f"{card} is already in place."
        steps.append({"move": [i, j + 1], "gold": [j + 1], "band": [0, i, "SORTED PART"], "eq": eq,
                      "chip": f"{card}: {len(bigger)}", "caption": cap})
    return steps


PASSES = len(EXAMPLE) - 1
SHIFTS = shifts(EXAMPLE)


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(22)
    cases = ["", "7", "2 1", "4 4 4", "1 2 3 4 5", "5 4 3 2 1", "2147483647 -2147483648 0", "5 2 4 1 3"]
    cases.append(" ".join(str(_r.randint(-10**9, 10**9)) for _ in range(1000)))
    for _ in range(1201):
        cases.append(" ".join(str(_r.randint(-20, 20)) for _ in range(_r.randint(0, 12))))
    return cases


def expected(line):
    return " ".join(map(str, sorted(int(x) for x in line.split())))
