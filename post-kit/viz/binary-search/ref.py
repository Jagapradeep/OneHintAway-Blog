"""Binary search on a sorted array (LeetCode 704): the reference for the website
visualizer. viz_steps() emits step schema v2 (an array view and a tree view) and
must match site/visualizer/patterns/binary-search.ts step for step."""
import importlib.util
from pathlib import Path

PATTERN = "binary-search"
EXAMPLE = {"nums": [1, 3, 5, 7, 9, 11], "target": 7}

PSEUDOCODE = [
    "function search(nums, target):",
    "    low = 0",
    "    high = length(nums) - 1",
    "    while low <= high:",
    "        middle = floor((low + high) / 2)",
    "        if nums[middle] == target:",
    "            return middle",
    "        else if nums[middle] < target:",
    "            low = middle + 1",
    "        else:",
    "            high = middle - 1",
    "    return -1",
]

L_START, L_MID, L_FOUND, L_LOW, L_HIGH, L_NONE = 2, 4, 6, 8, 10, 11
TREE_LABEL = "Every middle the search can check"


def solve(inp):
    nums, target = inp["nums"], inp["target"]
    low, high = 0, len(nums) - 1
    while low <= high:
        middle = low + (high - low) // 2
        if nums[middle] == target:
            return middle
        if nums[middle] < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1


def brute(inp):
    return inp["nums"].index(inp["target"]) if inp["target"] in inp["nums"] else -1


def same(inp, got, want):
    """With repeated numbers, any index that holds the target is right."""
    if want == -1:
        return got == -1
    return isinstance(got, int) and 0 <= got < len(inp["nums"]) and inp["nums"][got] == inp["target"]


def viz_steps(inp=EXAMPLE):
    nums, target = inp["nums"], inp["target"]
    low, high, middle = 0, len(nums) - 1, ""
    tried, steps = [], []

    def snap(line, say):
        focus = line in (L_MID, L_FOUND)
        found = line == L_FOUND

        def out(i):
            return i < low or i > high or found

        nodes = []
        todo = [(0, len(nums) - 1, None, None)]     # pre-order: a node, its left side, its right side
        while todo:
            lo, hi, parent, side = todo.pop()
            if lo > hi:
                continue
            m = lo + (hi - lo) // 2
            node = {"id": f"m{m}", "v": nums[m],
                    "state": "gold" if focus and m == middle else "steel" if m in tried else "dim" if out(m) else "plain"}
            if parent is not None:
                node["parent"], node["side"] = parent, side
            nodes.append(node)
            todo.append((m + 1, hi, f"m{m}", "right"))
            todo.append((lo, m - 1, f"m{m}", "left"))
        cells = [{"id": f"c{i}", "v": v, "state": "gold" if focus and i == middle else "dim" if out(i) else "plain"}
                 for i, v in enumerate(nums)]
        steps.append({"line": line, "say": say,
                      "views": [{"kind": "array", "id": "nums", "cells": cells,
                                 "pointers": [] if middle == "" else [{"id": "middle", "label": "middle", "at": middle}],
                                 "window": {"lo": low, "hi": high}},
                                {"kind": "tree", "id": "tree", "label": TREE_LABEL, "nodes": nodes}],
                      "vars": [{"name": "target", "value": target}, {"name": "low", "value": low},
                               {"name": "high", "value": high}, {"name": "middle", "value": middle}]})

    if not nums:
        snap(L_NONE, f"There are no numbers, so {target} is not here.")
        return steps
    snap(L_START, f"Look for {target}. It can be anywhere from index {low} to index {high}.")
    while low <= high:
        middle = low + (high - low) // 2
        tried.append(middle)
        v = nums[middle]
        snap(L_MID, f"The middle of index {low} to {high} is index {middle}. It holds {v}.")
        if v == target:
            snap(L_FOUND, f"{v} is the target. Found it at index {middle}.")
            return steps
        elif v < target:
            low = middle + 1
            snap(L_LOW, f"{v} is less than {target}: too small, so the left half goes. low = {low}.")
        else:
            high = middle - 1
            snap(L_HIGH, f"{v} is more than {target}: too big, so the right half goes. high = {high}.")
    snap(L_NONE, f"low has passed high: nothing is left to check, so {target} is not here.")
    return steps


def test_inputs():
    """Post 28's own test inputs ("target|numbers"), plus empty and repeated-number cases."""
    path = Path(__file__).resolve().parents[2] / "posts" / "28-binary-search" / "ref.py"
    spec = importlib.util.spec_from_file_location("post28_ref", path)
    post = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(post)
    cases = [
        {"nums": [], "target": 5},
        {"nums": [4, 4, 4, 4], "target": 4},
        {"nums": [4, 4, 4, 4], "target": 5},
        {"nums": [1, 2, 2, 2, 3, 3, 9], "target": 3},
        {"nums": list(range(1, 16)), "target": 15},
        {"nums": list(range(1, 16)), "target": 0},
        dict(EXAMPLE),
    ]
    for line in post.test_inputs():
        t, rest = line.split("|")
        cases.append({"nums": [int(x) for x in rest.split()], "target": int(t)})
    return cases
