# Reference for post 35 (LeetCode 54 and 48). Every number on the slides and in the video comes from here.

def rotate(grid):
    grid = [list(r) for r in grid]
    n = len(grid)
    for i in range(n):
        for j in range(i + 1, n):
            grid[i][j], grid[j][i] = grid[j][i], grid[i][j]
    for row in grid:
        row.reverse()
    return grid


def spiral_order(grid, guard=True, trace=None):
    top = 0
    bottom = len(grid) - 1
    left = 0
    right = len(grid[0]) - 1
    result = []

    def add(r, c, side):
        result.append(grid[r][c])
        if trace is not None:
            trace.append((r, c, side))
    while top <= bottom and left <= right:
        for col in range(left, right + 1):
            add(top, col, "top")
        top += 1
        for row in range(top, bottom + 1):
            add(row, right, "right")
        right -= 1
        if (top > bottom or left > right) and guard:
            return result
        for col in range(right, left - 1, -1):
            add(bottom, col, "bottom")
        bottom -= 1
        for row in range(bottom, top - 1, -1):
            add(row, left, "left")
        left += 1
    return result


def wrong_spiral(grid):
    """The trap: no check on line 21."""
    return spiral_order(grid, guard=False)


def brute_spiral(grid):
    """Walk and turn right when the next cell is outside or already seen."""
    m, n = len(grid), len(grid[0])
    seen = [[False] * n for _ in range(m)]
    moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    r = c = d = 0
    out = []
    for _ in range(m * n):
        out.append(grid[r][c])
        seen[r][c] = True
        nr, nc = r + moves[d][0], c + moves[d][1]
        if not (0 <= nr < m and 0 <= nc < n) or seen[nr][nc]:
            d = (d + 1) % 4
            nr, nc = r + moves[d][0], c + moves[d][1]
        r, c = nr, nc
    return out


def brute_rotate(grid):
    n = len(grid)
    return [[grid[n - 1 - j][i] for j in range(n)] for i in range(n)]


def sp(x):
    return " ".join(map(str, x))


GRID = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
FLAT = [v for row in GRID for v in row]
SPIRAL = spiral_order(GRID)
SQUARE = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
TRANSPOSED = [list(r) for r in zip(*SQUARE)]
ROTATED = rotate(SQUARE)
ORDER = [[0] * 4 for _ in range(3)]
for _k, _v in enumerate(SPIRAL):
    _i = FLAT.index(_v)
    ORDER[_i // 4][_i % 4] = _k + 1


def flat3(g):
    out = []
    for k, row in enumerate(g):
        out += row + ([""] if k < len(g) - 1 else [])
    return out


def video_steps(grid=GRID):
    cols = len(grid[0])
    trace = []
    spiral_order(grid, trace=trace)
    steps = [{"cuts": [3, 7], "eq": ["rows:", "3 × 4"], "caption": "Read the outside ring first, then go in."}]
    caps = {"top": "Top row, left to right. Then top moves down.",
            "right": "Right side, downwards. Then right moves in.",
            "bottom": "Bottom row, right to left. Bottom moves up.",
            "left": "Left side, upwards. Then left moves in."}
    done = []
    for k, (r, c, side) in enumerate(trace):
        slot = r * cols + c
        last = k + 1 == len(trace) or trace[k + 1][2] != side or (trace[k + 1][0], trace[k + 1][1]) == (r, c)
        done.append(slot)
        st = {"cuts": [3, 7], "gold": [slot], "steel": [x for x in done if x != slot],
              "eq": [f"grid[{r}][{c}] =", str(grid[r][c])], "caption": caps[side]}
        if last:
            st["chip"] = f"{side}: {len(_run(trace, k))}"
        else:
            st["quick"] = True
        steps.append(st)
    return steps


def _run(trace, k):
    side = trace[k][2]
    j = k
    while j - 1 >= 0 and trace[j - 1][2] == side:
        j -= 1
    return trace[j:k + 1]


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def _line(g):
    return f"{len(g)} {len(g[0])}|" + " ".join(str(v) for row in g for v in row)


def test_inputs():
    _r.seed(35)
    cases = [GRID, SQUARE, [[1]], [[1, 2, 3]], [[1], [2], [3]], [[1, 2], [3, 4]], [[1, 2, 3], [4, 5, 6]],
             [[-100, 100], [0, 5]], [[v for v in range(r * 10, r * 10 + 10)] for r in range(10)]]
    for _ in range(1300):
        m, n = _r.randint(1, 10), _r.randint(1, 10)
        if _r.random() < 0.4:
            n = m
        cases.append([[_r.randint(-100, 100) for _ in range(n)] for _ in range(m)])
    return [_line(g) for g in cases]


def expected(line):
    head, rest = line.split("|")
    m, n = map(int, head.split())
    v = list(map(int, rest.split()))
    g = [v[i * n:(i + 1) * n] for i in range(m)]
    rot = sp(v2 for row in brute_rotate(g) for v2 in row) if m == n else "-"
    return sp(brute_spiral(g)) + "|" + rot
