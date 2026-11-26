# Reference for post 21: factorial by recursion. Every number on the slides and in the video comes from here.
import sys


def factorial(n):
    if n == 0:
        return 1  # base case
    return n * factorial(n - 1)


def wrong_factorial(n):
    """The trap: base case n == 1, which factorial(0) skips straight past."""
    def f(k):
        if k == 1:
            return 1
        return k * f(k - 1)
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(200)
    try:
        return f(n)
    except RecursionError:
        return "stack overflow"
    finally:
        sys.setrecursionlimit(old)


def stack_height(n):
    return n + 1


EXAMPLE = [4, 3, 2, 1, 0]
ANSWER = factorial(4)
HEIGHT = stack_height(4)


def video_steps(n=4):
    calls = list(range(n, -1, -1))           # slot k holds the call factorial(n - k)
    steps = [{"gold": [0], "dim": list(range(1, n + 1)), "eq": ["factorial(4) =", "4 × factorial(3)"],
              "caption": "Each call waits for a smaller one."}]
    for k in range(1, n + 1):
        c = calls[k]
        eq = [f"factorial({c}) =", f"{c} × factorial({c - 1})"] if c else ["factorial(0) =", "1, base case"]
        steps.append({"gold": [k], "steel": list(range(k)), "dim": list(range(k + 1, n + 1)), "eq": eq,
                      "caption": "Each call waits for a smaller one." if c else "The base case answers straight away.", "quick": c > 0})
    val = 1
    steps[-1]["set"] = {str(n): 1}
    for k in range(n - 1, -1, -1):
        c = calls[k]
        val = c * val
        steps.append({"set": {str(k): val}, "gold": [k], "steel": list(range(k)), "dim": list(range(k + 1, n + 1)),
                      "eq": [f"{c} × {val // c} =", str(val)], "chip": f"f({c}) = {val}", "caption": "Answers come back, last call first."})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
def test_inputs():
    return [str(k) for k in range(0, 21)] * 60


def expected(line):
    n, out = int(line), 1
    for k in range(2, n + 1):
        out *= k
    return str(out)
