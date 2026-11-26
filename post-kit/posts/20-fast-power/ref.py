# Reference for post 20 (GeeksforGeeks Modular Exponentiation). Every number on the slides and in the video comes from here.

def power(x, n, m):
    answer = 1 % m
    block = x % m
    while n > 0:
        if n % 2 == 1:
            answer = (answer * block) % m
        block = (block * block) % m
        n = n // 2
    return answer


def wrong_power(x, n, m):
    """The trap: answer starts at 0, so every multiplication stays 0."""
    answer, block = 0, x % m
    while n > 0:
        if n % 2 == 1:
            answer = (answer * block) % m
        block = (block * block) % m
        n //= 2
    return answer


def rounds(n):
    c = 0
    while n > 0:
        c += 1
        n //= 2
    return c


X, N, M = 3, 13, 1000
ANSWER = power(X, N, M)
FULL = 3 ** 13
BLOCKS = [3, 9, 81, 6561 % 1000]
EXAMPLE = BLOCKS


def video_steps(x=X, n=N, m=M):
    answer, block, k = 1, x % m, 0
    steps = [{"eq": ["answer =", "1"], "caption": "Blocks: 3, then square it each round."}]
    while n > 0:
        odd = n % 2 == 1
        if odd:
            new = (answer * block) % m
            steps.append({"gold": [k], "steel": list(range(k)), "eq": [f"n = {n} odd →", f"{answer} × {block}"],
                          "caption": "n is odd: use this block.", "quick": True})
            answer = new
            steps.append({"gold": [k], "steel": list(range(k)), "eq": ["answer =", str(answer)], "chip": str(answer), "chip_hl": True,
                          "caption": "n is odd: use this block."})
        else:
            steps.append({"dim": [k], "steel": list(range(k)), "eq": [f"n = {n} even →", "skip"], "chip": str(answer),
                          "caption": "n is even: skip this block."})
        block = (block * block) % m
        n //= 2
        k += 1
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(20)
    cases = ["3 13 1000", "2 10 1000000007", "5 0 7", "0 5 7", "7 1 1", "10 18 1000000007", "999999999 999999999999 1000000007", "2 62 1000000007"]
    for _ in range(1300):
        cases.append(f"{_r.randint(0, 50)} {_r.randint(0, 60)} {_r.randint(1, 1000)}")
    for _ in range(50):
        cases.append(f"{_r.randint(0, 10**9)} {_r.randint(0, 10**12)} {_r.choice([1000000007, 998244353, 1000003])}")
    return cases


def expected(line):
    x, n, m = map(int, line.split())
    return str(pow(x, n, m))
