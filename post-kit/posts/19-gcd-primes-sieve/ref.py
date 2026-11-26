# Reference for post 19 (LeetCode 204, plus Euclid's GCD). Every number on the slides and in the video comes from here.

def count_primes(n):
    if n < 3:  # only 0 and 1 are below n
        return 0
    is_prime = [True] * n
    is_prime[0] = False
    is_prime[1] = False
    p = 2
    while p * p < n:
        if is_prime[p]:
            m = p * p
            while m < n:
                is_prime[m] = False
                m = m + p
        p = p + 1
    return sum(is_prime)


def wrong_count_primes(n):
    """The trap: 0 and 1 are never marked, so they get counted."""
    if n < 3:
        return 0
    is_prime = [True] * n
    p = 2
    while p * p < n:
        if is_prime[p]:
            for m in range(p * p, n, p):
                is_prime[m] = False
        p += 1
    return sum(is_prime)


def gcd(a, b):
    while b != 0:
        remainder = a % b
        a = b
        b = remainder
    return a


def primes_below(n):
    return [k for k in range(2, n) if all(k % d for d in range(2, int(k ** 0.5) + 1))]


N = 12
EXAMPLE = list(range(2, N))          # the boxes show 2 to 11
COUNT = count_primes(N)
PRIMES = primes_below(N)


def video_steps(n=N):
    vals = list(range(2, n))
    slot = lambda v: v - 2
    crossed = set()
    steps = [{"eq": ["numbers", f"2 to {n - 1}"], "caption": "Cross out multiples. Primes survive."}]
    p = 2
    while p * p < n:
        if p not in crossed:
            steps.append({"gold": [slot(p)], "dim": sorted(slot(x) for x in crossed), "steel": [slot(q) for q in range(2, p)],
                          "eq": [f"p = {p}, start at", f"{p * p}"], "caption": f"{p} is prime. Cross out its multiples."})
            for m in range(p * p, n, p):
                crossed.add(m)
                steps.append({"gold": [slot(p)], "dim": sorted(slot(x) for x in crossed), "steel": [slot(q) for q in range(2, p)],
                              "eq": [f"{m} = {p} × {m // p} →", "out"], "caption": f"{p} is prime. Cross out its multiples.", "quick": True})
            steps[-1].pop("quick")
            steps[-1]["chip"] = f"{p}: {len([m for m in range(p * p, n, p)])} out"
        p += 1
    steps.append({"dim": sorted(slot(x) for x in crossed), "steel": [slot(v) for v in vals if v not in crossed],
                  "eq": [f"{p} × {p} = {p * p} ≥ {n} →", "stop"], "caption": f"Past {p - 1}, every composite is already out."})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(19)
    cases = ["primes 12", "primes 10", "primes 0", "primes 1", "primes 2", "primes 3", "primes 30", "primes 5000000",
             "gcd 18 12", "gcd 12 18", "gcd 7 13", "gcd 5 0", "gcd 0 5", "gcd 1000000000 999999999", "gcd 1 1"]
    for _ in range(700):
        cases.append(f"primes {_r.randint(0, 2000)}")
    for _ in range(700):
        cases.append(f"gcd {_r.randint(0, 10**6)} {_r.randint(1, 10**6)}")
    return cases


def expected(line):
    w = line.split()
    if w[0] == "primes":
        n = int(w[1])
        if n > 100000:
            import math
            sieve = bytearray([1]) * n
            sieve[0:2] = b"\x00\x00"
            for i in range(2, math.isqrt(n - 1) + 1):
                if sieve[i]:
                    sieve[i * i::i] = bytearray(len(range(i * i, n, i)))
            return str(sum(sieve))
        return str(len(primes_below(n)))
    a, b = int(w[1]), int(w[2])
    return str(max(d for d in range(1, max(a, b) + 1) if a % d == 0 and b % d == 0)) if max(a, b) <= 2000 else str(__import__("math").gcd(a, b))
