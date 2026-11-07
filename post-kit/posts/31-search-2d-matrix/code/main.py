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


def cell(grid, i):
    """Index i of the grid read row after row."""
    cols = len(grid[0])
    row = i // cols
    col = i % cols
    return grid[row][col]
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    t, rc, rest = line.split("|")
    r, c = map(int, rc.split())
    v = [int(x) for x in rest.split()]
    g = [v[i * c:(i + 1) * c] for i in range(r)]
    print("true" if search_matrix(g, int(t)) else "false")
