"""Monotonic stack: the next greater number to the right of each number.
Reference for the website visualizer. viz_steps() emits step schema v1 and must
match site/visualizer/patterns/monotonic-stack.ts step for step."""
import random as _r

PATTERN = "monotonic-stack"
EXAMPLE = {"nums": [2, 1, 5, 3, 6]}

PSEUDOCODE = [
    "function nextGreater(nums):",
    "    answer = list of -1, same length as nums",
    "    stack = empty stack",
    "    for i from 0 to length(nums) - 1:",
    "        while stack is not empty and",
    "              nums[top of stack] < nums[i]:",
    "            waiting = pop from stack",
    "            answer[waiting] = nums[i]",
    "        push i onto stack",
    "    return answer",
]

L_START, L_POP, L_PUSH, L_DONE = 2, 7, 8, 9


def solve(inp):
    nums = inp["nums"]
    answer, stack = [-1] * len(nums), []
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            answer[stack.pop()] = x
        stack.append(i)
    return answer


def brute(inp):
    nums = inp["nums"]
    out = []
    for i, x in enumerate(nums):
        out.append(next((y for y in nums[i + 1:] if y > x), -1))
    return out


def _show(answer):
    return ", ".join(str(v).rjust(2) for v in answer)


def _state(i, at, answer, line):
    if line != L_DONE and i == at:
        return "gold"
    if answer[i] != -1:
        return "steel"
    return "dim" if line == L_DONE else "plain"


def viz_steps(inp=EXAMPLE):
    nums = inp["nums"]
    answer, stack, at = [-1] * len(nums), [], -1
    steps = []

    def snap(line, say):
        steps.append({"line": line, "say": say,
                      "cells": [{"v": v, "state": _state(i, at, answer, line)} for i, v in enumerate(nums)],
                      "pointers": [] if line == L_DONE or at < 0 else [{"id": "i", "label": "i", "at": at}],
                      "stack": [{"id": f"s{j}", "v": nums[j], "from": j} for j in stack],
                      "vars": [{"name": "answer", "value": _show(answer)}]})

    if not nums:
        snap(L_DONE, "There are no numbers, so the answer is empty.")
        return steps
    snap(L_START, "Every answer starts at -1. The stack of waiting numbers is empty.")
    for i in range(len(nums)):
        at = i
        while stack and nums[stack[-1]] < nums[i]:
            waiting = stack.pop()
            answer[waiting] = nums[i]
            snap(L_POP, f"{nums[waiting]} was waiting and {nums[i]} is bigger, so the answer for {nums[waiting]} is {nums[i]}.")
        if not stack:
            say = f"Nothing is waiting, so {nums[i]} goes onto the stack to wait."
        else:
            say = f"{nums[i]} is not bigger than {nums[stack[-1]]}, so {nums[i]} goes onto the stack to wait."
        stack.append(i)
        snap(L_PUSH, say)
    snap(L_DONE, "Nothing bigger came for the numbers still on the stack: they keep -1.")
    return steps


def test_inputs():
    _r.seed(31)
    cases = [
        {"nums": []},
        {"nums": [7]},
        {"nums": [0]},
        {"nums": [1, 2]},
        {"nums": [2, 1]},
        {"nums": [4, 4, 4, 4]},
        {"nums": [1, 2, 3, 4, 5]},
        {"nums": [5, 4, 3, 2, 1]},
        {"nums": [5, 4, 3, 2, 1, 6]},
        {"nums": [3, 3, 1, 3, 4]},
        {"nums": [0, 1000000000, 0, 999999999]},
        dict(EXAMPLE),
    ]
    cases.append({"nums": [_r.randint(0, 10**9) for _ in range(1000)]})
    cases.append({"nums": list(range(1000, 0, -1))})
    for _ in range(1300):
        cases.append({"nums": [_r.randint(0, 9) for _ in range(_r.randint(0, 12))]})
    return cases
