# Reference for post 36 (LeetCode 242 and 125). Every value on the slides and in the video comes from here.
from collections import Counter


def counts_after(s, t):
    counts = [0] * 26
    for letter in s:
        counts[ord(letter) - ord("a")] += 1
    for letter in t:
        counts[ord(letter) - ord("a")] -= 1
    return counts


def is_anagram(s, t):
    counts = counts_after(s, t)
    for count in counts:
        if count != 0:
            return False
    return True


def wrong_anagram(s, t):
    """The trap: count, then return true without checking the counts."""
    counts_after(s, t)
    return True


def is_palindrome(word):
    left = 0
    right = len(word) - 1
    while left < right:
        if word[left] != word[right]:
            return False
        left += 1
        right -= 1
    return True


def nonzero(s, t):
    return sum(1 for c in counts_after(s, t) if c != 0)


def tf(x):
    return "true" if x else "false"


S, T = "stone", "notes"
LETTERS = sorted(set(S))                  # e n o s t
INDEX_S = ord("s") - ord("a")


def video_steps(s=S, t=T):
    slot = {ch: i for i, ch in enumerate(LETTERS)}
    vals = [0] * len(LETTERS)
    steps = [{"eq": ["counts:", "all 0"], "caption": f"Count {s} up, then {t} down."}]
    for k, ch in enumerate(s):
        vals[slot[ch]] += 1
        st = {"set": {slot[ch]: vals[slot[ch]]}, "gold": [slot[ch]], "eq": [f"{ch} →", f"count[{ch}] = {vals[slot[ch]]}"],
              "caption": f"Read {s}: each letter adds 1."}
        if k == len(s) - 1:
            st["chip"] = f"{s}: +{len(s)}"
        else:
            st["quick"] = True
        steps.append(st)
    for k, ch in enumerate(t):
        vals[slot[ch]] -= 1
        st = {"set": {slot[ch]: vals[slot[ch]]}, "gold": [slot[ch]], "eq": [f"{ch} →", f"count[{ch}] = {vals[slot[ch]]}"],
              "caption": f"Read {t}: each letter takes 1 away."}
        if k == len(t) - 1:
            st["chip"] = f"{t}: −{len(t)}"
            st["chip_hl"] = True
        else:
            st["quick"] = True
        steps.append(st)
    labels = {ch: i for i, ch in enumerate(LETTERS)}
    for st in steps:
        st["ptr"] = dict(labels)
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(36)
    cases = [(S, T), ("stone", "note"), ("below", "elbow"), ("rat", "car"), ("anagram", "nagaram"), ("a", "a"),
             ("a", "b"), ("ab", "a"), ("aab", "abb"), ("racecar", "carrace"), ("level", "level"), ("abba", "baba"),
             ("z" * 50000, "z" * 50000), ("ab" * 25000, "ba" * 25000)]
    for _ in range(1300):
        n = _r.randint(1, 8)
        alpha = "abcde"[:_r.randint(1, 5)]
        s = "".join(_r.choice(alpha) for _ in range(n))
        r = _r.random()
        if r < 0.3:
            t = "".join(_r.sample(s, len(s)))
        elif r < 0.45:
            t = s[::-1]
            s = s + s[::-1] if _r.random() < 0.5 else s
        else:
            t = "".join(_r.choice(alpha) for _ in range(_r.randint(1, 8)))
        cases.append((s, t))
    return [f"{s}|{t}" for s, t in cases]


def expected(line):
    s, t = line.split("|")
    return tf(Counter(s) == Counter(t)) + " " + tf(s == s[::-1])
