def count_primes(n: int) -> int:
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

def gcd(a: int, b: int) -> int:
    while b != 0:
        remainder = a % b
        a = b
        b = remainder
    return a
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    w = line.split()
    print(count_primes(int(w[1])) if w[0] == "primes" else gcd(int(w[1]), int(w[2])))
