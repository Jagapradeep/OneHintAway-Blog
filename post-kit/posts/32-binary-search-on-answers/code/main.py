def min_speed(piles, hours):
    low = 1
    high = max(piles)
    while low < high:
        speed = (low + high) // 2
        if hours_at(piles, speed) <= hours:
            high = speed  # fast enough
        else:
            low = speed + 1  # too slow
    return low


def hours_at(piles, speed):
    total = 0
    for pile in piles:
        total += (pile + speed - 1) // speed  # ceil(pile / speed)
    return total
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    h, rest = line.split("|")
    print(min_speed([int(x) for x in rest.split()], int(h)))
