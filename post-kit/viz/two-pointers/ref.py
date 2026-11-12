"""Two pointers on a sorted array (LeetCode 167): the reference for the website
visualizer. viz_steps() emits step schema v2 and must match
site/visualizer/patterns/two-pointers.ts step for step."""
import random as _r

PATTERN = "two-pointers"
EXAMPLE = {"numbers": [1, 3, 4, 6, 8, 11], "target": 10}

PSEUDOCODE = [
    "function twoSum(numbers, target):",
    "    left = 0",
    "    right = length(numbers) - 1",
    "    while left < right:",
    "        total = numbers[left] + numbers[right]",
    "        if total == target:",
    "            return [left + 1, right + 1]",
    "        else if total < target:",
    "            left = left + 1",
    "        else:",
    "            right = right - 1",
    "    return none",
]

L_START, L_TOTAL, L_FOUND, L_LEFT, L_RIGHT, L_NONE = 2, 4, 6, 8, 10, 11


def solve(inp):
    nums, target = inp["numbers"], inp["target"]
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return [left + 1, right + 1]
        if total < target:
            left += 1
        else:
            right -= 1
    return None


def brute(inp):
    nums, target = inp["numbers"], inp["target"]
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i + 1, j + 1]
    return None


def same(inp, got, want):
    """More than one pair can add up to the target: any correct pair counts."""
    if got is None or want is None:
        return got is want
    a, b = got
    return 1 <= a < b <= len(inp["numbers"]) and inp["numbers"][a - 1] + inp["numbers"][b - 1] == inp["target"]


def viz_steps(inp=EXAMPLE):
    nums, target = inp["numbers"], inp["target"]
    left, right = 0, len(nums) - 1
    steps = []

    def snap(line, say, total):
        found = line == L_FOUND
        cells = [{"id": f"c{i}", "v": v, "state": "gold" if i in (left, right) else "dim" if i < left or i > right or found else "plain"}
                 for i, v in enumerate(nums)]
        pointers = [{"id": "left", "label": "left", "at": left}, {"id": "right", "label": "right", "at": right}] if nums else []
        steps.append({"line": line, "say": say,
                      "views": [{"kind": "array", "id": "numbers", "cells": cells, "pointers": pointers}],
                      "vars": [{"name": "target", "value": target}, {"name": "total", "value": total}]})

    if not nums:
        snap(L_NONE, f"There are no numbers, so no pair adds up to {target}.", "")
        return steps
    snap(L_START, "left starts on the first number, right on the last.", "")
    while left < right:
        total = nums[left] + nums[right]
        snap(L_TOTAL, f"Add the two ends: {nums[left]} + {nums[right]} = {total}.", total)
        if total == target:
            snap(L_FOUND, f"{total} is the target. Found it: positions {left + 1} and {right + 1}.", total)
            return steps
        elif total < target:
            left += 1
            snap(L_LEFT, f"{total} is less than {target}: too small, so left moves one step in.", total)
        else:
            right -= 1
            snap(L_RIGHT, f"{total} is more than {target}: too big, so right moves one step in.", total)
    snap(L_NONE, f"left and right have met. No pair adds up to {target}.", "")
    return steps


def test_inputs():
    _r.seed(6)
    cases = [
        {"numbers": [], "target": 5},
        {"numbers": [7], "target": 7},
        {"numbers": [7], "target": 14},
        {"numbers": [2, 7], "target": 9},
        {"numbers": [2, 7], "target": 10},
        {"numbers": [4, 4, 4, 4], "target": 8},
        {"numbers": [4, 4, 4, 4], "target": 9},
        {"numbers": [-5, -3, 0, 2, 9], "target": -8},
        {"numbers": [-5, -3, 0, 2, 9], "target": 0},
        {"numbers": [1, 2, 3, 4, 5], "target": 9},
        {"numbers": [1, 2, 3, 4, 5], "target": 3},
        {"numbers": [1, 2, 3, 4, 5], "target": 100},
        {"numbers": [-1000000000, 0, 1000000000], "target": 0},
        {"numbers": [-1000000000, 1000000000], "target": 2000000000},
        dict(EXAMPLE),
    ]
    big = sorted(_r.randint(-10**9, 10**9) for _ in range(1000))
    cases.append({"numbers": big, "target": big[311] + big[702]})
    cases.append({"numbers": big, "target": 3 * 10**9})
    for _ in range(1300):
        n = _r.randint(0, 12)
        nums = sorted(_r.randint(-20, 20) for _ in range(n))
        if n >= 2 and _r.random() < 0.6:
            i, j = _r.sample(range(n), 2)
            target = nums[i] + nums[j]
        else:
            target = _r.randint(-45, 45)
        cases.append({"numbers": nums, "target": target})
    return cases
