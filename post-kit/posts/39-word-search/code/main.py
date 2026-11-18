MOVES = [(1, 0), (-1, 0), (0, 1), (0, -1)]  # down, up, right, left


def walk(grid, word, row, col, i):
    if grid[row][col] != word[i]:
        return False
    if i == len(word) - 1:
        return True
    grid[row][col] = "#"  # in use
    for dr, dc in MOVES:  # each cell next to [row, col]
        r, c = row + dr, col + dc
        if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
            if walk(grid, word, r, c, i + 1):
                return True
    grid[row][col] = word[i]  # undo
    return False


def exist(grid, word):
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if walk(grid, word, row, col, 0):
                return True
    return False
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    w, rows = line.split("|")
    print("true" if exist([list(r) for r in rows.split("/")], w) else "false")
