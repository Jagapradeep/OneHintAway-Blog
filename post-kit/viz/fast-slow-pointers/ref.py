"""Fast and slow pointers (LeetCode 141 and 876, post 42): the reference for the
website visualizer. The trace runs hasCycle; with no loop it ends with slow on the
middle node, which is what middleNode returns. viz_steps() emits step schema v2
with the list view and must match site/visualizer/patterns/fast-slow-pointers.ts
step for step. solve() walks real nodes; brute() follows the list by hand and
remembers every node it has seen."""
import random as _r

PATTERN = "fast-slow-pointers"
EXAMPLE = {"nums": [1, 2, 3, 4, 5, 6], "loop": 2}

PSEUDOCODE = [
    "function middleNode(head):",
    "    slow = head",
    "    fast = head",
    "    while fast != none and fast.next != none:",
    "        slow = slow.next",
    "        fast = fast.next.next",
    "    return slow",
    "",
    "function hasCycle(head):",
    "    slow = head",
    "    fast = head",
    "    while fast != none and fast.next != none:",
    "        slow = slow.next        // 1 step",
    "        fast = fast.next.next   // 2 steps",
    "        if slow == fast:",
    "            return true   // a loop",
    "    return false",
]

LABEL = "Linked list"


class Node:
    def __init__(self, val):
        self.val, self.next = val, None


def solve(inp):
    nodes = [Node(v) for v in inp["nums"]]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    if inp["loop"] >= 0:
        nodes[-1].next = nodes[inp["loop"]]
    slow = fast = nodes[0]
    while fast is not None and fast.next is not None:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            return True
    return False


def brute(inp):
    n, seen, at = len(inp["nums"]), set(), 0
    while at >= 0:
        if at in seen:
            return True
        seen.add(at)
        at = at + 1 if at + 1 < n else inp["loop"]
    return False


def viz_steps(inp):
    vals, loop = inp["nums"], inp["loop"]
    n = len(vals)
    after = lambda i: -1 if i < 0 else i + 1 if i + 1 < n else loop
    name = lambda i: "none" if i < 0 else str(vals[i])
    st = {"slow": 0, "fast": 0, "round": 0}
    steps = []

    def snap(line, say):
        slow, fast = st["slow"], st["fast"]
        nodes = [{"id": f"n{i}", "v": v, "next": None if after(i) < 0 else f"n{after(i)}",
                  "state": "gold" if i == slow else "steel" if i == fast else "plain"} for i, v in enumerate(vals)]
        pointers = [{"id": "slow", "label": "slow", "at": None if slow < 0 else f"n{slow}"},
                    {"id": "fast", "label": "fast", "at": None if fast < 0 else f"n{fast}"}]
        steps.append({"line": line, "say": say,
                      "views": [{"kind": "list", "id": "list", "label": LABEL, "nodes": nodes, "pointers": pointers}],
                      "vars": [{"name": "round", "value": st["round"]}]})

    snap(10, f"slow and fast both start on the head, {vals[0]}.")
    while st["fast"] >= 0 and after(st["fast"]) >= 0:
        st["round"] += 1
        st["slow"] = after(st["slow"])
        snap(12, f"Round {st['round']}: slow moves 1 step, to {name(st['slow'])}.")
        st["fast"] = after(after(st["fast"]))
        same = st["fast"] == st["slow"]
        snap(13, f"fast moves 2 steps, to {name(st['fast'])}" + (": the same node as slow." if same else "."))
        if same:
            snap(15, f"They meet on {vals[st['slow']]}: the list loops. Return true.")
            return steps
    snap(11, "fast is none: it ran off the end." if st["fast"] < 0
         else f"fast is on {vals[st['fast']]}, the last node: it can't take 2 steps.")
    snap(16, f"No loop: return false. slow stands on {vals[st['slow']]}, the middle node.")
    return steps


def test_inputs():
    _r.seed(142)
    cases = [dict(EXAMPLE), {"nums": [1, 2, 3, 4, 5, 6], "loop": -1}, {"nums": [5], "loop": -1},
             {"nums": [5], "loop": 0}, {"nums": [1, 2], "loop": 0}, {"nums": [1, 2], "loop": 1}]
    while len(cases) < 1300:
        n = _r.randint(1, 8)
        cases.append({"nums": [_r.randint(-99, 99) for _ in range(n)],
                      "loop": -1 if _r.random() < 0.4 else _r.randint(0, n - 1)})
    return cases
