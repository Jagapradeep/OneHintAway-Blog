# Reference for post 42 (LeetCode 141 and 876). Every value on the slides and in the video comes from here.


class Node:
    def __init__(self, val):
        self.val, self.next = val, None


def build(vals, pos=-1):
    nodes = [Node(v) for v in vals]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    if pos >= 0 and nodes:
        nodes[-1].next = nodes[pos]
    return nodes[0] if nodes else None, nodes


def has_cycle(head, trace=None):
    slow = head
    fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if trace is not None:
            trace.append((slow.val, fast.val))
        if slow is fast:
            return True
    return False


def middle_node(head):
    slow = head
    fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    return slow


def wrong_has_cycle(head):
    """The trap: only checks fast.next, so it crashes when fast itself is none."""
    slow = fast = head
    try:
        while fast.next is not None:
            slow = slow.next
            fast = fast.next.next
            if slow is fast:
                return "true"
        return "false"
    except AttributeError:
        return "error"


def tf(x):
    return "true" if x else "false"


LIST = [1, 2, 3, 4, 5, 6]
POS = 2                                       # 6 links back to 3
TRACE = []
has_cycle(build(LIST, POS)[0], TRACE)
MEET = TRACE[-1][0]
ROUNDS = len(TRACE)
MIDDLE = middle_node(build(LIST)[0]).val


def video_steps(vals=LIST):
    idx = {v: i for i, v in enumerate(vals)}
    band = [POS, len(vals) - 1, "LOOP"]
    steps = [{"band": band, "ptr": {"slow": 0, "fast": 0}, "eq": ["slow = fast =", str(vals[0])],
              "caption": "Slow takes 1 step a round, fast takes 2."}]
    prev_s, prev_f = vals[0], vals[0]
    for k, (s, f) in enumerate(TRACE):
        wrap = idx[f] < idx[prev_f]
        cap = f"Fast runs {vals[-1]} → {vals[POS]}: back into the loop." if wrap else "Slow takes 1 step a round, fast takes 2."
        steps.append({"band": band, "ptr": {"slow": idx[s], "fast": idx[prev_f]}, "gold": [idx[s]],
                      "eq": ["slow →", str(s)], "caption": cap, "quick": True})
        meet = s == f
        steps.append({"band": band, "ptr": {"slow": idx[s], "fast": idx[f]}, "gold": [idx[s]], "steel": [] if meet else [idx[f]],
                      "eq": ["fast →", str(f)] if not meet else ["slow == fast →", "loop"],
                      "caption": f"Both on {s}: fast caught up, so there is a loop." if meet else cap,
                      "chip": f"{s}·{f}", "chip_hl": meet})
        prev_s, prev_f = s, f
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(42)
    cases = [(LIST, POS), (LIST, -1), ([1, 2, 3, 4, 5], -1), ([3, 2, 0, -4], 1), ([1, 2], 0), ([1], -1), ([1], 0), ([], -1),
             (list(range(10000)), 0), (list(range(10000)), 9999), (list(range(10000)), -1)]
    for _ in range(1300):
        n = _r.randint(1, 12)
        vals = [_r.randint(-100000, 100000) for _ in range(n)]
        cases.append((vals, _r.randint(0, n - 1) if _r.random() < 0.5 else -1))
    return [" ".join(map(str, v)) + f"|{p}" for v, p in cases]


def expected(line):
    v, p = line.split("|")
    vals, pos = v.split(), int(p)
    if pos >= 0:
        return "true"
    return "false " + (vals[len(vals) // 2] if vals else "none")
