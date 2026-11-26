# Reference for post 16 (LeetCode 56). Every number on the slides and in the video comes from here.

def merge(intervals):
    intervals = sorted([list(p) for p in intervals], key=lambda pair: pair[0])
    merged = []
    merged.append([intervals[0][0], intervals[0][1]])
    for i in range(1, len(intervals)):
        start, end = intervals[i]
        last = merged[-1]
        if start <= last[1]:                # overlap
            last[1] = max(last[1], end)
        else:
            merged.append([start, end])
    return merged


def wrong_merge(intervals):
    """The trap: last[1] = end, so a booking inside the block shrinks it."""
    intervals = sorted([list(p) for p in intervals], key=lambda pair: pair[0])
    merged = [list(intervals[0])]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = end
        else:
            merged.append([start, end])
    return merged


def fmt(blocks):
    return ", ".join(f"[{a}, {b}]" for a, b in blocks)


EXAMPLE = [[5, 8], [1, 3], [8, 9], [6, 7], [2, 4]]
SORTED = sorted(EXAMPLE)
MERGED = merge(EXAMPLE)
WRONG = wrong_merge(EXAMPLE)
LABELS = [f"{a}–{b}" for a, b in SORTED]


def video_steps(blocks=SORTED):
    vals = [f"{a}–{b}" for a, b in blocks]
    steps = [{"eq": ["sorted by", "start"], "caption": "Sorted by start. Stretch or start a block."}]
    owner = 0
    last = list(blocks[0])
    absorbed = []
    steps.append({"gold": [0], "eq": ["block", f"[{last[0]}, {last[1]}]"], "caption": "The first booking starts the first block."})
    for i in range(1, len(blocks)):
        s, e = blocks[i]
        if s <= last[1]:
            new_end, old_end = max(last[1], e), last[1]
            steps.append({"gold": [owner], "steel": [i], "dim": list(absorbed), "eq": [f"{s} ≤ {last[1]} →", "overlap"],
                          "caption": f"{s} starts before {last[1]} ends: join.", "quick": True})
            last[1] = new_end
            absorbed.append(i)
            steps.append({"set": {str(owner): f"{last[0]}–{last[1]}"}, "gold": [owner], "dim": list(absorbed),
                          "eq": ["end = max →", str(last[1])], "chip": f"[{last[0]}, {last[1]}]", "caption": f"{s} starts before {old_end} ends: join."})
        else:
            steps.append({"gold": [i], "steel": [owner], "dim": list(absorbed), "eq": [f"{s} > {last[1]} →", "new block"],
                          "chip": f"[{s}, {e}]", "chip_hl": True, "caption": f"{s} starts after {last[1]}: a new block."})
            owner, last = i, [s, e]
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(16)
    cases = ["13 17, 9 11, 18 19, 14 15, 10 12", "1 3, 2 6, 8 10, 15 18", "1 4, 4 5", "2 4, 1 3, 6 8", "1 4, 2 3", "5 5", "0 0, 0 0", "1 10, 2 3, 4 5, 6 7"]
    for _ in range(1300):
        n = _r.randint(1, 8)
        ps = []
        for _ in range(n):
            a = _r.randint(0, 20); ps.append(f"{a} {a + _r.randint(0, 6)}")
        cases.append(", ".join(ps))
    ps = []
    for _ in range(2000):
        a = _r.randint(0, 10**4); ps.append(f"{a} {a + _r.randint(0, 10)}")
    cases.append(", ".join(ps))
    return cases


def expected(line):
    ps = [tuple(map(int, p.split())) for p in line.split(",")]
    covered = set()
    for a, b in ps:
        for x in range(2 * a, 2 * b + 1):
            covered.add(x)
    out, xs = [], sorted(covered)
    start = prev = xs[0]
    for x in xs[1:]:
        if x != prev + 1:
            out.append((start // 2, prev // 2)); start = x
        prev = x
    out.append((start // 2, prev // 2))
    return ", ".join(f"{a} {b}" for a, b in out)
