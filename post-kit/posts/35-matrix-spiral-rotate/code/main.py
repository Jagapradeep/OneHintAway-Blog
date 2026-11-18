def rotate(grid):
    n = len(grid)
    for i in range(n):
        for j in range(i + 1, n):
            grid[i][j], grid[j][i] = grid[j][i], grid[i][j]
    for row in grid:
        row.reverse()


def spiral_order(grid):
    top = 0
    bottom = len(grid) - 1
    left = 0
    right = len(grid[0]) - 1
    result = []
    while top <= bottom and left <= right:
        for col in range(left, right + 1):
            result.append(grid[top][col])
        top += 1
        for row in range(top, bottom + 1):
            result.append(grid[row][right])
        right -= 1
        if top > bottom or left > right:
            return result  # nothing left
        for col in range(right, left - 1, -1):
            result.append(grid[bottom][col])
        bottom -= 1
        for row in range(bottom, top - 1, -1):
            result.append(grid[row][left])
        left += 1
    return result
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    head, rest = line.split("|")
    m, n = map(int, head.split())
    v = list(map(int, rest.split()))
    g = [v[i * n:(i + 1) * n] for i in range(m)]
    s = " ".join(map(str, spiral_order(g)))
    r = "-"
    if m == n:
        rotate(g)
        r = " ".join(str(x) for row in g for x in row)
    print(s + "|" + r)
