# Reference for post 39 (LeetCode 79). Every value on the slides and in the video comes from here.

MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1)]       # down, up, right, left


def walk(grid, word, row, col, i, mark=True):
    if grid[row][col] != word[i]:
        return False
    if i == len(word) - 1:
        return True
    if mark:
        grid[row][col] = "#"
    for dr, dc in MOVES:
        r, c = row + dr, col + dc
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
            if walk(grid, word, r, c, i + 1, mark):
                return True
    if mark:
        grid[row][col] = word[i]
    return False


def exist(grid, word, mark=True):
    g = [list(r) for r in grid]
    for row in range(len(g)):
        for col in range(len(g[0])):
            if walk(g, word, row, col, 0, mark):
                return True
    return False


def wrong_exist(grid, word):
    """The trap: no line 5, so a cell can be used twice."""
    return exist(grid, word, mark=False)


def brute(grid, word):
    """Every simple path of the right length, from every cell, with a set of used cells."""
    m, n = len(grid), len(grid[0])

    def go(r, c, i, used):
        if grid[r][c] != word[i]:
            return False
        if i == len(word) - 1:
            return True
        for dr, dc in MOVES:
            a, b = r + dr, c + dc
            if 0 <= a < m and 0 <= b < n and (a, b) not in used:
                if go(a, b, i + 1, used | {(a, b)}):
                    return True
        return False
    return any(go(r, c, 0, {(r, c)}) for r in range(m) for c in range(n))


def tf(x):
    return "true" if x else "false"


GRID = [["C", "A", "T"], ["A", "R", "T"]]
WORD = "CAT"
FLAT = [v for row in GRID for v in row]


def video_steps():
    cut = {"cuts": [2]}
    s = []
    s.append(dict(cut, eq=["word =", WORD], caption="Find CAT. Each letter must touch the last."))
    cap1 = "Start at C. Try down first."
    s.append(dict(cut, gold=[0], eq=["word[0] = C →", "match"], caption=cap1, quick=True))
    s.append(dict(cut, set={0: "#"}, steel=[0], eq=["grid[0][0] =", "#"], caption="Mark C as in use, then go down."))
    s.append(dict(cut, steel=[0], gold=[3], eq=["word[1] = A →", "match"], caption="Down: A matches. Mark it too.", quick=True))
    s.append(dict(cut, set={3: "#"}, steel=[0, 3], eq=["grid[1][0] =", "#"], caption="Down: A matches. Mark it too."))
    s.append(dict(cut, steel=[0, 3], gold=[4], eq=["need T, see R →", "no"], caption="Next to it: # above, R on the right."))
    s.append(dict(cut, set={3: "A"}, steel=[0], dim=[3], eq=["undo →", "A is free again"],
                  caption="Dead end. Undo and go back to C.", chip="down: no"))
    s.append(dict(cut, steel=[0], gold=[1], eq=["word[1] = A →", "match"], caption="Right: A matches. Mark it.", quick=True))
    s.append(dict(cut, set={1: "#"}, steel=[0, 1], eq=["grid[0][1] =", "#"], caption="Right: A matches. Mark it."))
    s.append(dict(cut, steel=[0, 1], gold=[2], eq=["word[2] = T →", "found"], caption="Right again: T. The word is there.",
                  chip="right: yes", chip_hl=True))
    return s


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def _line(g, w):
    return f"{w}|" + "/".join("".join(r) for r in g)


def test_inputs():
    _r.seed(39)
    lc = [list("ABCE"), list("SFCS"), list("ADEE")]
    cases = [(GRID, "CAT"), (GRID, "CAC"), (GRID, "CART"), (GRID, "TRAC"), (GRID, "ART"), (GRID, "TAT"),
             (lc, "ABCCED"), (lc, "SEE"), (lc, "ABCB"), ([["a"]], "a"), ([["a"]], "b"), ([["a", "a"]], "aaa"),
             ([list("aaaaaa") for _ in range(6)], "aaaaaaaaaaaaaab"), ([list("aaaaaa") for _ in range(6)], "a" * 15)]
    for _ in range(1300):
        m, n = _r.randint(1, 4), _r.randint(1, 4)
        alpha = "abc"[:_r.randint(1, 3)]
        g = [[_r.choice(alpha) for _ in range(n)] for _ in range(m)]
        w = "".join(_r.choice(alpha) for _ in range(_r.randint(1, 6)))
        cases.append((g, w))
    return [_line(g, w) for g, w in cases]


def expected(line):
    w, rows = line.split("|")
    return tf(brute([list(r) for r in rows.split("/")], w))
