# Reference for post 38 (LeetCode 46 and 39). Every value on the slides and in the video comes from here.
from itertools import permutations as _perms


def permute(nums, used, path, out, events=None):
    if len(path) == len(nums):
        out.append(list(path))
        if events is not None:
            events.append(("save", list(path)))
        return out
    for i in range(len(nums)):
        if not used[i]:
            used[i] = True
            path.append(nums[i])
            if events is not None:
                events.append(("choose", nums[i]))
            permute(nums, used, path, out, events)
            path.pop()
            used[i] = False
            if events is not None:
                events.append(("undo", nums[i]))
    return out


def find(nums, i, left, path, out, start_at_zero=False):
    if left == 0:
        out.append(list(path))
        return out
    for j in range(i, len(nums)):
        if nums[j] <= left:
            path.append(nums[j])
            rest = left - nums[j]
            find(nums, 0 if start_at_zero else j, rest, path, out, start_at_zero)
            path.pop()
    return out


def perms(nums):
    return permute(nums, [False] * len(nums), [], [])


def combos(nums, target):
    return find(nums, 0, target, [], [])


def wrong_combos(nums, target):
    """The trap: recurse with 0 instead of j."""
    return find(nums, 0, target, [], [], start_at_zero=True)


def show(lists, limit=None):
    items = ["[" + " ".join(map(str, x)) + "]" for x in lists]
    if limit and len(items) > limit:
        items = items[:limit] + ["…"]
    return " ".join(items)


NUMS = [1, 2, 3]
PERMS = perms(NUMS)
CANDS, TARGET = [2, 3, 6, 7], 7
COMBOS = combos(CANDS, TARGET)


def video_steps(nums=NUMS):
    events = []
    permute(nums, [False] * len(nums), [], [], events)
    n = len(nums)
    path = []
    steps = [{"dash": list(range(n)), "eq": ["seats:", "empty"], "caption": "Fill seat 1, then 2, then 3."}]
    saves = 0
    k = 0
    while k < len(events) and saves < 2:
        kind, v = events[k]
        if kind == "save":
            k += 1
            continue
        if kind == "choose":
            path.append(v)
            eq = [f"choose {v} →", " ".join(map(str, path))]
        else:
            path.pop()
            eq = [f"undo {v} →", " ".join(map(str, path)) or "empty"]
        vals = path + [""] * (n - len(path))
        st = {"set": {s: vals[s] for s in range(n)}, "dash": [s for s in range(n) if vals[s] == ""],
              "gold": [len(path) - 1] if kind == "choose" else [], "eq": eq,
              "caption": "Choose, go deeper, then undo to try again." if saves else "Choose a value for each seat."}
        if k + 1 < len(events) and events[k + 1][0] == "save":
            saves += 1
            st["chip"] = "".join(map(str, events[k + 1][1]))
            st["chip_hl"] = True
            k += 1
        else:
            st["quick"] = True
        steps.append(st)
        k += 1
    rest = PERMS[2:]
    for p in rest:
        steps.append({"set": {s: p[s] for s in range(n)}, "gold": [0], "eq": ["seat 1 =", str(p[0])],
                      "caption": "Same moves with 2 first, then 3 first.", "chip": "".join(map(str, p)), "chip_hl": True,
                      "hold": 0.6})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(38)
    cases = ["P|1 2 3", "P|1", "P|0 1", "P|-10 10 0", "P|1 2 3 4 5 6", "P|6 5 4 3 2 1",
             "C|7|2 3 6 7", "C|8|2 3 5", "C|1|2", "C|1|1", "C|30|2 3 5 7", "C|30|10 20 30"]
    for _ in range(500):
        n = _r.randint(1, 6)
        cases.append("P|" + " ".join(map(str, _r.sample(range(-10, 11), n))))
    for _ in range(800):
        n = _r.randint(1, 6)
        c = sorted(_r.sample(range(2, 15), n)) if _r.random() < 0.7 else _r.sample(range(2, 15), n)
        cases.append(f"C|{_r.randint(1, 25)}|" + " ".join(map(str, c)))
    return cases


def _fmt(lists):
    return ",".join(" ".join(map(str, x)) for x in lists)


def expected(line):
    parts = line.split("|")
    if parts[0] == "P":
        nums = [int(x) for x in parts[1].split()]
        return _fmt([list(p) for p in _perms(nums)])
    target = int(parts[1])
    nums = [int(x) for x in parts[2].split()]
    found = []

    def counts(k, left, idx):          # how many of each number, in index order
        if left == 0:
            found.append(tuple(idx))
            return
        if k == len(nums):
            return
        c = 0
        while c * nums[k] <= left:
            counts(k + 1, left - c * nums[k], idx + [k] * c)
            c += 1
    counts(0, target, [])
    found.sort()
    return _fmt([[nums[t] for t in idx] for idx in found])
