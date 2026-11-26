# Post 02: every step count the videos show is measured by running these functions.
import math

def one_pass(nums):
    steps = 0
    for x in nums:
        steps += 1
    return steps

def two_passes(nums):
    steps = 0
    for x in nums:
        steps += 1
    for x in nums:
        steps += 1
    return steps

def every_pair(nums):
    steps = 0
    for x in nums:
        for y in nums:
            steps += 1
    return steps

def halvings(n):
    steps = 0
    while n > 1:
        n = n // 2
        steps += 1
    return steps

def looks_sorted(n):
    """Binary search on n sorted sheets: looks needed in the worst case."""
    lo, hi, worst = 0, n - 1, 0
    def depth(lo, hi):
        if lo > hi:
            return 0
        mid = (lo + hi) // 2
        return 1 + max(depth(lo, mid - 1), depth(mid + 1, hi))
    return depth(0, n - 1)

R = {n: list(range(n)) for n in (10, 100, 1000)}
ONE = {n: one_pass(R[n]) for n in R}
TWO = {n: two_passes(R[n]) for n in R}
PAIR = {n: every_pair(R[n]) for n in R}
HALF = {n: halvings(n) for n in R}
HALF_MILLION = halvings(1_000_000)
LOOKS = looks_sorted(1000)
