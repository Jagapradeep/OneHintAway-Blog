# Reference for post 37 (LeetCode 78). Every value on the slides and in the video comes from here.

def build(nums, i, picked, out, events=None, copy=True):
    if i == len(nums):
        out.append(list(picked) if copy else picked)
        if events is not None:
            events.append(("save", list(picked)))
    else:
        picked.append(nums[i])
        if events is not None:
            events.append(("pick", nums[i]))
        build(nums, i + 1, picked, out, events, copy)
        picked.pop()
        if events is not None:
            events.append(("undo", nums[i]))
        build(nums, i + 1, picked, out, events, copy)


def subsets(nums):
    out = []
    build(nums, 0, [], out)
    return out


def wrong_subsets(nums):
    """The trap: add picked itself, not a copy."""
    out = []
    build(nums, 0, [], out, copy=False)
    return out


def brute(nums):
    """Every bitmask, index 0 as the highest bit, from all-picked down to none."""
    n = len(nums)
    res = []
    for mask in range((1 << n) - 1, -1, -1):
        res.append([nums[i] for i in range(n) if mask >> (n - 1 - i) & 1])
    return res


def show(lists, limit=None):
    items = ["[" + " ".join(map(str, x)) + "]" for x in lists]
    if limit and len(items) > limit:
        items = items[:limit] + ["…"]
    return " ".join(items)


NUMS = [1, 2, 3]
ALL = subsets(NUMS)
COUNT = len(ALL)


def video_steps(nums=NUMS):
    events = []
    build(nums, 0, [], [], events)
    n = len(nums)
    picked = []
    steps = [{"dash": list(range(n)), "eq": ["picked:", "empty"], "caption": "For each value: pick it, then skip it."}]
    k = 0
    while k < len(events):
        kind, v = events[k]
        if kind == "save":
            k += 1
            continue
        if kind == "pick":
            picked.append(v)
            eq = [f"pick {v} →", " ".join(map(str, picked))]
        else:
            picked.pop()
            eq = [f"skip {v} →", " ".join(map(str, picked)) or "empty"]
        vals = picked + [""] * (n - len(picked))
        if picked[:1] == [1] or (kind == "pick" and v == 1):
            cap = "Subsets that pick 1."
        elif kind == "undo" and v == 1:
            cap = "Undo 1: now the subsets that skip 1."
        else:
            cap = "Subsets that skip 1."
        st = {"set": {s: vals[s] for s in range(n)}, "dash": [s for s in range(n) if vals[s] == ""],
              "gold": [len(picked) - 1] if kind == "pick" else [], "eq": eq, "caption": cap}
        if k + 1 < len(events) and events[k + 1][0] == "save":
            st["chip"] = "".join(map(str, events[k + 1][1])) or "∅"
            st["chip_hl"] = True
            k += 1
        else:
            st["quick"] = True
        steps.append(st)
        k += 1
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(37)
    cases = [NUMS, [0], [5], [1, 2], [-10, 10], [9, 0, 3, 4], list(range(1, 11)), list(range(-10, 0))]
    for _ in range(1300):
        n = _r.randint(1, 8)
        cases.append(_r.sample(range(-10, 11), n))
    return [" ".join(map(str, c)) for c in cases]


def expected(line):
    return ",".join(" ".join(map(str, s)) for s in brute([int(x) for x in line.split()]))
