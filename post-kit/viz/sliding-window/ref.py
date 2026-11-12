"""Sliding window of any size (post 08): the longest run whose total stays within
the budget. Reference for the website visualizer. viz_steps() emits step schema
v1 and must match site/visualizer/patterns/sliding-window.ts step for step."""
import random as _r

PATTERN = "sliding-window"
EXAMPLE = {"nums": [2, 1, 3, 1, 4], "budget": 5}

PSEUDOCODE = [
    "function longestWithin(nums, budget):",
    "    left = 0",
    "    total = 0",
    "    best = 0",
    "    for right from 0 to length(nums) - 1:",
    "        total = total + nums[right]",
    "        while total > budget:",
    "            total = total - nums[left]",
    "            left = left + 1",
    "        best = max(best, right - left + 1)",
    "    return best",
]

L_START, L_GROW, L_SHRINK, L_MEASURE, L_DONE = 3, 5, 8, 9, 10


def solve(inp):
    nums, budget = inp["nums"], inp["budget"]
    left = total = best = 0
    for right in range(len(nums)):
        total += nums[right]
        while total > budget:
            total -= nums[left]
            left += 1
        best = max(best, right - left + 1)
    return best


def brute(inp):
    nums, budget = inp["nums"], inp["budget"]
    best = 0
    for i in range(len(nums)):
        total = 0
        for j in range(i, len(nums)):
            total += nums[j]
            if total <= budget:
                best = max(best, j - i + 1)
    return best


def _state(i, lo, hi, line):
    if line == L_DONE:
        return "gold" if lo <= i <= hi else "dim"
    if i < lo:
        return "dim"
    if i > hi:
        return "plain"
    return "gold" if line == L_GROW and i == hi else "steel"


def viz_steps(inp=EXAMPLE):
    nums, budget = inp["nums"], inp["budget"]
    left, right, total, best, best_left = 0, -1, 0, 0, 0
    steps = []

    def snap(line, say):
        done = line == L_DONE
        lo = best_left if done else left
        hi = best_left + best - 1 if done else right
        shown = sum(nums[lo:hi + 1]) if done else total
        pointers = []
        if not done and left < len(nums):
            pointers.append({"id": "left", "label": "left", "at": left})
        if not done and right >= 0:
            pointers.append({"id": "right", "label": "right", "at": right})
        steps.append({"line": line, "say": say,
                      "cells": [{"v": v, "state": _state(i, lo, hi, line)} for i, v in enumerate(nums)],
                      "pointers": pointers, "window": {"lo": lo, "hi": hi},
                      "vars": [{"name": "budget", "value": budget}, {"name": "total", "value": shown}, {"name": "best", "value": best}]})

    if not nums:
        snap(L_DONE, "There are no numbers, so the longest window is 0.")
        return steps
    snap(L_START, "The window starts empty: total 0, best 0.")
    for right in range(len(nums)):
        total += nums[right]
        snap(L_GROW, f"{nums[right]} joins the window: total is {total}.")
        while total > budget:
            before = total
            total -= nums[left]
            left += 1
            snap(L_SHRINK, f"{before} is over the budget {budget}, so {nums[left - 1]} leaves: total is {total}.")
        length = right - left + 1
        if length > best:
            best, best_left = length, left
            snap(L_MEASURE, f"The window fits. Its length is {length}: a new best.")
        else:
            snap(L_MEASURE, f"The window fits. Its length is {length}, so best stays {best}.")
    snap(L_DONE, f"Every number has joined once. The longest window that fits has length {best}.")
    return steps


def test_inputs():
    _r.seed(8)
    cases = [
        {"nums": [], "budget": 5},
        {"nums": [7], "budget": 7},
        {"nums": [7], "budget": 6},
        {"nums": [7], "budget": 0},
        {"nums": [3, 3, 3, 3], "budget": 6},
        {"nums": [3, 3, 3, 3], "budget": 2},
        {"nums": [1, 2, 3, 4, 5], "budget": 15},
        {"nums": [1, 2, 3, 4, 5], "budget": 100},
        {"nums": [5, 4, 3, 2, 1], "budget": 6},
        {"nums": [1, 1, 1, 9], "budget": 3},
        {"nums": [9, 1, 1, 1], "budget": 3},
        {"nums": [4, 9], "budget": 5},
        {"nums": [1000000000, 1000000000, 1], "budget": 2000000000},
        dict(EXAMPLE),
    ]
    big = [_r.randint(1, 10**6) for _ in range(1000)]
    cases.append({"nums": big, "budget": 25 * 10**6})
    cases.append({"nums": big, "budget": 0})
    for _ in range(1300):
        n = _r.randint(0, 12)
        cases.append({"nums": [_r.randint(1, 12) for _ in range(n)], "budget": _r.randint(0, 30)})
    return cases
