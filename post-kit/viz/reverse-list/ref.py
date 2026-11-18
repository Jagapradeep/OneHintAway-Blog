"""Reverse a linked list (LeetCode 206, post 41): the reference for the website
visualizer. viz_steps() emits step schema v2 with the list view and must match
site/visualizer/patterns/reverse-list.ts step for step. solve() walks real nodes;
brute() just reverses the values."""
import random as _r

PATTERN = "reverse-list"
EXAMPLE = {"nums": [1, 2, 3, 4, 5]}

PSEUDOCODE = [
    "function reverseList(head):",
    "    prev = none",
    "    curr = head",
    "    while curr != none:",
    "        rest = curr.next   // save it",
    "        curr.next = prev   // turn the arrow",
    "        prev = curr",
    "        curr = rest",
    "    return prev",
]

LABEL = "Linked list"


class Node:
    def __init__(self, val, nxt=None):
        self.val, self.next = val, nxt


def solve(inp):
    head = None
    for v in reversed(inp["nums"]):
        head = Node(v, head)
    prev, curr = None, head
    while curr is not None:
        rest = curr.next
        curr.next = prev
        prev, curr = curr, rest
    out = []
    while prev is not None:
        out.append(prev.val)
        prev = prev.next
    return out


def brute(inp):
    return list(reversed(inp["nums"]))


def viz_steps(inp):
    vals = inp["nums"]
    n = len(vals)
    nxt = [i + 1 if i + 1 < n else None for i in range(n)]
    name = lambda i: "none" if i < 0 or i >= n else str(vals[i])
    nid = lambda i: None if i < 0 or i >= n else f"n{i}"
    st = {"prev": -1, "curr": 0, "rest": None}
    steps = []

    def snap(line, say):
        prev, curr, rest = st["prev"], st["curr"], st["rest"]
        nodes = [{"id": f"n{i}", "v": v, "next": None if nxt[i] is None else f"n{nxt[i]}",
                  "state": "gold" if i == curr else "steel" if i < curr or i <= prev else "plain"}
                 for i, v in enumerate(vals)]
        pointers = [{"id": "prev", "label": "prev", "at": nid(prev)},
                    {"id": "curr", "label": "curr", "at": nid(curr)}]
        if rest is not None:
            pointers.append({"id": "rest", "label": "rest", "at": nid(rest)})
        steps.append({"line": line, "say": say,
                      "views": [{"kind": "list", "id": "list", "label": LABEL, "nodes": nodes, "pointers": pointers}],
                      "vars": []})

    snap(2, f"prev starts as none, and curr on the head, {vals[0]}.")
    while st["curr"] < n:
        c = st["curr"]
        st["rest"] = c + 1
        snap(4, f"Save the rest of the list: rest = {name(c + 1)}.")
        nxt[c] = None if st["prev"] < 0 else st["prev"]
        snap(5, f"Turn {vals[c]}'s arrow back: it now points to {name(st['prev'])}.")
        st["prev"] = c
        snap(6, f"prev = curr: the turned part now starts at {vals[c]}.")
        st["curr"] = c + 1
        snap(7, f"curr = rest: move on to {name(c + 1)}.")
    snap(3, "curr is none, so the loop stops.")
    out = list(reversed(vals))
    snap(8, f"Return prev, {vals[st['prev']]}: the list now reads {' '.join(map(str, out))}.")
    return steps


def test_inputs():
    _r.seed(141)
    cases = [dict(EXAMPLE), {"nums": [7]}, {"nums": [1, 2]}, {"nums": [3, 3, 3]}, {"nums": [-99, 99, 0, -1, 1, 50, -50]}]
    while len(cases) < 1200:
        cases.append({"nums": [_r.randint(-99, 99) for _ in range(_r.randint(1, 7))]})
    return cases
