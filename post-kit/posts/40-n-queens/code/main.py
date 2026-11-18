def safe(queens, row, col):
    for r in range(row):
        c = queens[r]
        gap = row - r
        if col == c:
            return False  # same column
        if col == c + gap or col == c - gap:
            return False  # same diagonal
    return True


def place(queens, row, n, out):
    if row == n:
        out.append(["." * q + "Q" + "." * (n - q - 1) for q in queens])  # a board drawn from queens
        return
    for col in range(n):
        if safe(queens, row, col):
            queens[row] = col  # a queen
            place(queens, row + 1, n, out)


def solve_n_queens(n):
    out = []
    place([0] * n, 0, n, out)
    return out
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    p = line.split("|")
    if p[0] == "N":
        print("|".join(",".join(b) for b in solve_n_queens(int(p[1]))))
    else:
        q = [int(x) for x in p[1].split()]
        print("true" if safe(q, int(p[2]), int(p[3])) else "false")
