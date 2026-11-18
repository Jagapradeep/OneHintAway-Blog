# Reference for post 40 (LeetCode 51). Every value on the slides and in the video comes from here.
from itertools import permutations as _perms
from math import comb


def safe(queens, row, col):
    for r in range(row):
        c = queens[r]
        gap = row - r
        if col == c:
            return False
        if col == c + gap or col == c - gap:
            return False
    return True


def draw(queens, n):
    return ["." * q + "Q" + "." * (n - q - 1) for q in queens]


def place(queens, row, n, out, events=None, stop_after=None):
    if row == n:
        out.append(draw(queens, n))
        if events is not None:
            events.append(("found", list(queens)))
        return
    any_safe = False
    for col in range(n):
        if stop_after and len(out) >= stop_after:
            return
        if safe(queens, row, col):
            any_safe = True
            queens[row] = col
            if events is not None:
                events.append(("place", row, col))
            place(queens, row + 1, n, out, events, stop_after)
            if events is not None and not (stop_after and len(out) >= stop_after):
                events.append(("lift", row, col))
    if events is not None and not any_safe:
        events.append(("stuck", row))


def solve(n):
    out = []
    place([0] * n, 0, n, out)
    return out


def brute(n):
    res = []
    for p in _perms(range(n)):
        if all(abs(p[i] - p[j]) != j - i for i in range(n) for j in range(i + 1, n)):
            res.append(draw(p, n))
    return res


def attacked(queens_placed, n, row, col):
    """Is (row, col) attacked by any placed queen (a dict row -> col)?"""
    return any(c == col or abs(c - col) == abs(r - row) for r, c in queens_placed.items() if r != row)


N = 4
SOLS = solve(N)
FIRST = [row.index("Q") for row in SOLS[0]]
BOARDS_ALL = comb(N * N, N)
BOARDS_8 = comb(64, 8)


def tf(x):
    return "true" if x else "false"


def video_steps(n=N):
    events = []
    place([0] * n, 0, n, [], events, stop_after=1)
    placed = {}
    steps = [{"dash": list(range(n)), "eq": ["queens placed:", "0"], "caption": "One queen per row, starting at row 0."}]

    def state(gold=None, extra=None):
        vals = [placed.get(r, "") for r in range(n)]
        st = {"set": {r: vals[r] for r in range(n)}, "dash": [r for r in range(n) if vals[r] == ""],
              "steel": [r for r in placed if r != gold]}
        if gold is not None:
            st["gold"] = [gold]
        if extra:
            st.update(extra)
        return st

    recent = set()
    k = 0
    while k < len(events):
        ev = events[k]
        if ev[0] == "place":
            _, r, c = ev
            moved = r in placed or r in recent
            recent = {x for x in recent if x < r}
            placed[r] = c
            cap = f"Row {r}: column {c} is safe." if not moved else f"Back up: row {r} tries column {c}."
            steps.append(state(r, {"eq": [f"row {r} →", f"col {c}"], "caption": cap}))
        elif ev[0] == "stuck":
            r = ev[1]
            steps.append(state(None, {"eq": [f"row {r} →", "all attacked"],
                                      "caption": f"Row {r}: every column is attacked. Back up.",
                                      "chip": " ".join(str(placed[x]) for x in sorted(placed)) + " ✗"}))
        elif ev[0] == "lift":
            lifted = []
            while k < len(events) and events[k][0] in ("lift", "stuck"):
                if events[k][0] == "lift":
                    lifted.append(events[k][1])
                    placed.pop(events[k][1], None)
                k += 1
            recent |= set(lifted)
            if len(lifted) > 1:
                steps.append(state(None, {"eq": ["lift rows", " ".join(map(str, sorted(lifted)))],
                                          "caption": "Rows 2 and 1 run out too: back to row 0."}))
            continue
        elif ev[0] == "found":
            steps[-1]["chip"] = " ".join(map(str, ev[1])) + " ✓"
            steps[-1]["chip_hl"] = True
            steps[-1]["caption"] = "Row 3: column 2 is safe. All 4 placed."
        k += 1
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(40)
    cases = [f"N|{n}" for n in range(1, 10)]
    cases += ["S|0 2|2|1", "S|1 3|2|0", "S|0|1|1", "S|0|1|2", "S||0|0", "S|1 3 0|3|2", "S|1 3 0|3|1"]
    for _ in range(1300):
        n = _r.randint(1, 9)
        row = _r.randint(0, n - 1)
        q = [_r.randint(0, n - 1) for _ in range(row)]
        cases.append(f"S|{' '.join(map(str, q))}|{row}|{_r.randint(0, n - 1)}")
    return cases


def expected(line):
    p = line.split("|")
    if p[0] == "N":
        return "|".join(",".join(b) for b in brute(int(p[1])))
    q = [int(x) for x in p[1].split()]
    row, col = int(p[2]), int(p[3])
    return tf(not any(q[r] == col or abs(q[r] - col) == row - r for r in range(row)))


def safe_cols(queens, row, n):
    cols = [c for c in range(n) if safe(queens, row, c)]
    return " and ".join(map(str, cols)) if cols else "none"
