# Reference for post 09 (LeetCode 76). Every number and letter on the slides and in the video comes from here.
from collections import Counter


def min_window(s, t):
    need = {}
    for c in t:
        need[c] = need.get(c, 0) + 1
    missing = len(t)
    left = 0
    best_start = 0
    best_len = float("inf")
    for right in range(len(s)):
        c = s[right]
        if need.get(c, 0) > 0:
            missing = missing - 1
        need[c] = need.get(c, 0) - 1
        while missing == 0:
            if right - left + 1 < best_len:
                best_start = left
                best_len = right - left + 1
            d = s[left]
            need[d] = need[d] + 1
            if need[d] > 0:
                missing = missing + 1
            left = left + 1
    if best_len == float("inf"):
        return ""
    return s[best_start:best_start + best_len]


def wrong_min_window(s, t):
    """The trap: lower missing for every letter that joins, needed or not (one changed line)."""
    need = {}
    for c in t:
        need[c] = need.get(c, 0) + 1
    missing, left, best_start, best_len = len(t), 0, 0, float("inf")
    for right in range(len(s)):
        c = s[right]
        missing = missing - 1
        need[c] = need.get(c, 0) - 1
        while missing == 0:
            if right - left + 1 < best_len:
                best_start, best_len = left, right - left + 1
            d = s[left]
            need[d] = need[d] + 1
            if need[d] > 0:
                missing = missing + 1
            left = left + 1
    return "" if best_len == float("inf") else s[best_start:best_start + best_len]


WRONG_DEMO = None


S, T = "ABDBCA", "ABC"
EXAMPLE = list(S)
BEST = min_window(S, T)
LEET = min_window("ADOBECODEBANC", "ABC")
WRONG = wrong_min_window(S, T)


def video_steps(s=S, t=T):
    need = Counter(t)
    missing, left, best = len(t), 0, None
    grow = "Grow until nothing is missing."
    shrink = "Shrink while nothing is missing."
    steps = [{"eq": ["missing =", str(missing)], "caption": "Find the shortest part with A, B and C."}]
    for right, c in enumerate(s):
        if need[c] > 0:
            missing -= 1
        need[c] -= 1
        steps.append({"frame": [left, right], "ptr": {"left": left, "right": right}, "gold": [right], "dim": list(range(left)),
                      "eq": [f"{c} joins →", f"missing {missing}"], "caption": grow})
        while missing == 0:
            w = s[left:right + 1]
            if best is None or len(w) < len(best):
                best = w
                steps.append({"frame": [left, right], "ptr": {"left": left, "right": right}, "dim": list(range(left)),
                              "eq": ["record", f"{w} · {len(w)}"], "chip": w, "chip_hl": True, "caption": shrink})
            d = s[left]
            need[d] += 1
            if need[d] > 0:
                missing += 1
            left += 1
            steps.append({"frame": [left, right] if left <= right else None, "ptr": {"left": left, "right": right},
                          "dim": list(range(left)), "eq": [f"{d} leaves →", f"missing {missing}"], "caption": shrink, "hold": 0.5})
    for st in steps:
        if st.get("frame") is None:
            st.pop("frame", None)
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(9)
    cases = ["ABDBCA ABC", "ADOBECODEBANC ABC", "a a", "a aa", "ab b", "aa aa", "abc d", "bba ab", "cabwefgewcwaefgcf cae"]
    for _ in range(1300):
        al = "ABCD"[: _r.randint(2, 4)]
        s = "".join(_r.choice(al) for _ in range(_r.randint(1, 12)))
        t = "".join(_r.choice(al) for _ in range(_r.randint(1, 4)))
        cases.append(f"{s} {t}")
    s = "".join(_r.choice("abcdefgh") for _ in range(400))
    cases.append(f"{s} {''.join(_r.choice('abcdefgh') for _ in range(12))}")
    return cases


def expected(line):
    s, t = line.split()
    need = Counter(t)
    for L in range(1, len(s) + 1):
        for i in range(len(s) - L + 1):
            if not (need - Counter(s[i:i + L])):
                return s[i:i + L]
    return "-"
