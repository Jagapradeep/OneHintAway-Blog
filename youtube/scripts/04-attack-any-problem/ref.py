# Post 04: LeetCode 121, brute force and one pass, checked against each other on random inputs.
import random

def max_profit_brute(prices):
    n, best = len(prices), 0
    for buy in range(n):
        for sell in range(buy + 1, n):
            best = max(best, prices[sell] - prices[buy])
    return best

def max_profit(prices):
    cheapest, best = prices[0], 0
    for price in prices:
        cheapest = min(cheapest, price)
        best = max(best, price - cheapest)
    return best

def walk(prices):
    cheapest, best, rows = prices[0], 0, []
    for price in prices:
        cheapest = min(cheapest, price)
        best = max(best, price - cheapest)
        rows.append((price, cheapest, best))
    return rows

P = [7, 1, 5, 3, 6, 4]
ANSWER = max_profit(P)
W = walk(P)
PRICE, CHEAP, BEST = [r[0] for r in W], [r[1] for r in W], [r[2] for r in W]
EDGES = {"[5]": max_profit([5]), "[7, 6, 4, 3, 1]": max_profit([7, 6, 4, 3, 1]), "[2, 2, 2]": max_profit([2, 2, 2])}
N = 10 ** 5
PAIRS = N * N                      # 10,000,000,000
PER_SECOND = 10 ** 8

rng = random.Random(4)
TESTED = 0
for _ in range(2000):
    arr = [rng.randint(0, 20) for _ in range(rng.randint(1, 12))]
    assert max_profit(arr) == max_profit_brute(arr), arr
    TESTED += 1

def row(xs):
    return xs
