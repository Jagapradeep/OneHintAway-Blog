"""Word search (LeetCode 79, post 39): brute-force answers for the website
visualizer's build check.

The step-by-step picture lives in site/visualizer/patterns/word-search.ts. This
file only says what the right answer is, without backtracking: for each letter
list the tiles that hold it, try every combination, and keep one whose tiles are
all different and each next to the one before.
(No viz_steps() here: the fixture then carries the example's answer, not a step trace.)"""
import itertools
import random as _r

PATTERN = "word-search"
EXAMPLE = {"letters": "CATART", "cols": 3, "word": "CAT"}


def brute(inp):
    letters, cols, word = inp["letters"].upper(), inp["cols"], inp["word"].upper()
    where = [[k for k, ch in enumerate(letters) if ch == w] for w in word]
    near = lambda a, b: abs(a // cols - b // cols) + abs(a % cols - b % cols) == 1
    for path in itertools.product(*where):
        if len(set(path)) == len(path) and all(near(a, b) for a, b in zip(path, path[1:])):
            return True
    return False


def test_inputs():
    _r.seed(139)
    cases = [dict(EXAMPLE), {"letters": "CATART", "cols": 3, "word": "TRAC"}, {"letters": "CATART", "cols": 3, "word": "CAC"},
             {"letters": "A", "cols": 1, "word": "A"}, {"letters": "A", "cols": 1, "word": "AA"},
             {"letters": "AAAAAA", "cols": 3, "word": "AAAB"}, {"letters": "AAAAAA", "cols": 2, "word": "AAAA"}]
    while len(cases) < 1200:
        cols = _r.randint(1, 3)
        rows = _r.randint(1, min(3, 6 // cols))
        abc = "AB" if _r.random() < 0.3 else "ABCDE"
        letters = "".join(_r.choice(abc) for _ in range(rows * cols))
        if _r.random() < 0.5:
            # a word read along a random walk, so many inputs are found
            k = _r.randrange(rows * cols)
            word = letters[k]
            for _ in range(_r.randint(0, 3)):
                r, c = divmod(k, cols)
                opts = [(r + dr) * cols + c + dc for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))
                        if 0 <= r + dr < rows and 0 <= c + dc < cols]
                k = _r.choice(opts) if opts else k
                word += letters[k]
        else:
            word = "".join(_r.choice(abc) for _ in range(_r.randint(1, 4)))
        cases.append({"letters": letters, "cols": cols, "word": word})
    return cases
