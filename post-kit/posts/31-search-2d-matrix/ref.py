# Reference for post 31 (LeetCode 74). Every number on the slides and in the video comes from here.

def cell(grid, i):
    cols = len(grid[0])
    row = i // cols
    col = i % cols
    return grid[row][col]


def search_matrix(grid, target):
    cells = len(grid) * len(grid[0])
    low = 0
    high = cells - 1
    while low <= high:
        middle = (low + high) // 2
        if cell(grid, middle) == target:
            return True
        elif cell(grid, middle) < target:
            low = middle + 1
        else:
            high = middle - 1
    return False


def wrong_cell(grid, i):
    """The trap: rows and columns mixed up, so the grid is read column by column."""
    rows = len(grid)
    row = i % rows
    col = i // rows
    return grid[row][col]


def wrong_search(grid, target):
    cells = len(grid) * len(grid[0])
    low, high = 0, cells - 1
    while low <= high:
        middle = (low + high) // 2
        v = wrong_cell(grid, middle)
        if v == target:
            return True
        elif v < target:
            low = middle + 1
        else:
            high = middle - 1
    return False


def rc(i, cols):
    return f"row {i // cols}, column {i % cols}"


def tf(b):
    return "true" if b else "false"


GRID = [[1, 3, 5], [7, 9, 11]]
FLAT = [v for row in GRID for v in row]
TARGET = 11
FOUND = tf(search_matrix(GRID, TARGET))
AT = FLAT.index(TARGET)


def video_steps(grid=GRID, target=TARGET):
    cols = len(grid[0])
    flat = [v for row in grid for v in row]
    low, high = 0, len(flat) - 1
    steps = [{"frame": [low, high], "eq": ["target =", str(target)],
              "caption": "Read the grid as one sorted row of 6 cells."}]
    while low <= high:
        m = (low + high) // 2
        v = flat[m]
        st = {"frame": [low, high], "gold": [m], "eq": [f"index {m} → {rc(m, cols)}", str(v)], "chip": f"{m} → {v}"}
        if v == target:
            st.update({"chip_hl": True, "caption": f"Index {m} is {rc(m, cols)}: {v}. Found."})
            steps.append(st)
            break
        if v < target:
            st["caption"] = f"{v} < {target}: go right. low = {m + 1}."
            low = m + 1
        else:
            st["caption"] = f"{v} > {target}: go left. high = {m - 1}."
            high = m - 1
        steps.append(st)
    return steps


# ---- video dressing: LOW / MID / HIGH labels, discarded side dimmed ----
def _dress(steps, n):
    for st in steps:
        fr = st.get("frame")
        if not fr:
            continue
        lo, hi = fr
        out = [i for i in range(n) if i < lo or i > hi]
        if out:
            st["dim"] = sorted(set(st.get("dim", []) + out))
        old = st.get("ptr") or {}
        ptr = {"low": old.get("low", lo)}
        if st.get("gold"):
            ptr["mid"] = st["gold"][0]
        ptr["high"] = old.get("high", hi)
        st["ptr"] = ptr
    return steps


def _narrow(steps):
    """After each check, a short step of its own: the range shrinks before the next middle appears."""
    out = []
    for k, st in enumerate(steps):
        out.append(st)
        nx = steps[k + 1] if k + 1 < len(steps) else None
        if not (nx and st.get("gold") and st.get("frame") and nx.get("frame")) or nx["frame"] == st["frame"]:
            continue
        (a, b), (c, d) = st["frame"], nx["frame"]
        if c < a or d > b:                  # a new search starts: not a shrink
            continue
        mid = {"frame": [c, d], "eq": st["eq"], "caption": st["caption"], "hold": 0.5}
        if st.get("steel") == [b]:
            mid["steel"] = [d]
        out.append(mid)
    return out


_raw_video_steps = video_steps


def video_steps(*args, **kw):
    return _dress(_narrow(_raw_video_steps(*args, **kw)), len(GRID) * len(GRID[0]))


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def _line(t, grid):
    return f"{t}|{len(grid)} {len(grid[0])}|" + " ".join(str(v) for row in grid for v in row)


def test_inputs():
    _r.seed(31)
    cases = [_line(11, GRID), _line(9, GRID), _line(1, GRID), _line(4, GRID), _line(0, GRID), _line(12, GRID),
             _line(3, [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]),
             _line(13, [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]),
             _line(5, [[5]]), _line(6, [[5]]), _line(2, [[1], [2], [3]]), _line(4, [[1, 2, 3]]),
             _line(-10000, [[-10000, 10000]]), _line(10000, [[-10000], [10000]])]
    vals = sorted(_r.sample(range(-10000, 10001), 10000))
    g = [vals[i * 100:(i + 1) * 100] for i in range(100)]
    cases.append(_line(vals[4321], g))
    cases.append(_line(vals[4321] + 1 if vals[4321] + 1 not in vals else 10001, g))
    for _ in range(1200):
        r, c = _r.randint(1, 4), _r.randint(1, 4)
        vals = sorted(_r.sample(range(-30, 31), r * c))
        g = [vals[i * c:(i + 1) * c] for i in range(r)]
        t = _r.choice(vals) if _r.random() < 0.5 else _r.randint(-32, 32)
        cases.append(_line(t, g))
    return cases


def expected(line):
    t, rc_, rest = line.split("|")
    return tf(int(t) in [int(x) for x in rest.split()])
MAX_CHECKS = (100 * 100).bit_length()   # worst case for 100 x 100 cells
