# Reference for post 41 (LeetCode 206). Every value on the slides and in the video comes from here.


class Node:
    def __init__(self, val, nxt=None):
        self.val, self.next = val, nxt


def build(vals):
    head = None
    for v in reversed(vals):
        head = Node(v, head)
    return head


def to_list(head, limit=100):
    out = []
    while head is not None and len(out) < limit:
        out.append(head.val)
        head = head.next
    return out


def reverse_list(head, trace=None):
    prev = None
    curr = head
    while curr is not None:
        rest = curr.next
        curr.next = prev
        if trace is not None:
            trace.append((curr.val, prev.val if prev else None, rest.val if rest else None))
        prev = curr
        curr = rest
    return prev


def wrong_reverse(head):
    """The trap: no saved rest; move with curr = curr.next after the flip."""
    prev = None
    curr = head
    while curr is not None:
        curr.next = prev
        prev = curr
        curr = curr.next
    return prev


def sp(x):
    return " ".join(map(str, x)) if x else "empty"


def after_loops(vals, k):
    head = build(vals)
    prev, curr = None, head
    for _ in range(k):
        rest = curr.next
        curr.next = prev
        prev, curr = curr, rest
    return f"{prev.val if prev else 'none'} and {curr.val if curr else 'none'}"


LIST = [1, 2, 3, 4, 5]
REVERSED = to_list(reverse_list(build(LIST)))
WRONG = to_list(wrong_reverse(build(LIST)))


def video_steps(vals=LIST):
    """Slot 0 is none; slots 1..n are the nodes. The steel band is the reversed part."""
    n = len(vals)
    trace = []
    reverse_list(build(vals), trace)
    steps = [{"ptr": {"prev": 0, "curr": 1}, "eq": ["prev = none,", "curr = 1"],
              "caption": "Flip each arrow to point back, one node at a time."}]
    for k, (c, p, r) in enumerate(trace):
        slot = k + 1
        cap = f"Save the rest, then point {c} back at {p if p is not None else 'none'}."
        ptr = {"prev": slot - 1, "curr": slot}
        if r is not None:
            ptr["rest"] = slot + 1
        steps.append({"ptr": ptr, "gold": [slot], "steel": list(range(1, slot)),
                      "eq": [f"{c}.next →", str(p) if p is not None else "none"], "caption": cap})
        ptr2 = {"prev": slot}
        if slot + 1 <= n:
            ptr2["curr"] = slot + 1
        steps.append({"ptr": ptr2, "steel": list(range(1, slot + 1)), "eq": ["move", "prev, curr"],
                      "caption": cap, "quick": True})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(41)
    cases = [LIST, [], [7], [1, 2], [5, 5, 5], [-5000, 5000], list(range(5000))]
    for _ in range(1300):
        cases.append([_r.randint(-5000, 5000) for _ in range(_r.randint(0, 12))])
    return [" ".join(map(str, c)) for c in cases]


def expected(line):
    return " ".join(reversed(line.split()))
