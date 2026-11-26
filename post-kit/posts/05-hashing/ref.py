# Reference for post 05 (LeetCode 1). Every number on the slides and in the video comes from here.

def two_sum(nums, target):
    seen = {}                      # value -> index
    for i in range(len(nums)):
        need = target - nums[i]
        if need in seen:
            return [seen[need], i]
        seen[nums[i]] = i
    return None


def wrong_two_sum(nums, target):
    """The trap: store first, then check, so a number can pair with itself."""
    seen = {}
    for i in range(len(nums)):
        seen[nums[i]] = i
        need = target - nums[i]
        if need in seen:
            return [seen[need], i]
    return None


def count_letters(word):
    counts = {}
    for ch in word:
        counts[ch] = counts.get(ch, 0) + 1
    return counts


def looks(nums, target):
    """How many numbers the one pass looks at before it returns."""
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return i + 1
        seen[x] = i
    return len(nums)


EXAMPLE = [3, 8, 4, 6, 1]
TARGET = 10
ANSWER = two_sum(EXAMPLE, TARGET)
LOOKS = looks(EXAMPLE, TARGET)
PAIRS = len(EXAMPLE) * (len(EXAMPLE) - 1) // 2
BANANA = ", ".join(f"{k}: {v}" for k, v in count_letters("banana").items())


def video_steps(nums=EXAMPLE, target=TARGET):
    """One step per number: the pointer lands on it, its partner is worked out, the map is checked,
    then the number is remembered (steel). The found pair ends gold and steel."""
    steps = [{"eq": ["target =", str(target)], "caption": "Walk once. Remember every number seen."}]
    seen = {}
    for i, x in enumerate(nums):
        need = target - x
        done = sorted(seen.values())
        if need in seen:
            steps.append({"ptr": {"i": i}, "gold": [i], "steel": done, "eq": [f"need {target} − {x} =", str(need)],
                          "caption": f"Need {need}. It was seen at index {seen[need]}.", "quick": True})
            steps.append({"ptr": {"i": i}, "gold": [seen[need], i], "eq": [f"{need} seen →", f"[{seen[need]}, {i}]"],
                          "caption": f"Need {need}. It was seen at index {seen[need]}."})
            return steps
        steps.append({"ptr": {"i": i}, "gold": [i], "steel": done, "eq": [f"need {target} − {x} =", str(need)],
                      "caption": f"Need {need}. Not seen yet, so remember {x}."})
        seen[x] = i
        steps.append({"ptr": {"i": i}, "steel": sorted(seen.values()), "eq": [f"remember {x} →", f"index {i}"],
                      "chip": f"{x} → {i}", "caption": f"Need {need}. Not seen yet, so remember {x}.", "quick": True})
    return steps


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(5)
    cases = ["10 | 3 8 4 6 1", "6 | 3 2 4", "6 | 3 3", "9 | 2 7 11 15", "5 | 1", "0 | 0 0", "-2 | -1 -1",
             "2000000000 | 1000000000 1000000000", "-2000000000 | -1000000000 -1000000000", "7 | 1 2 3", "4 | 2 2 2 2"]
    for _ in range(1300):
        n = _r.randint(1, 12)
        a = [_r.randint(-20, 20) for _ in range(n)]
        t = _r.randint(-40, 40) if _r.random() < 0.4 else (a[_r.randrange(n)] + a[_r.randrange(n)])
        cases.append(f"{t} | " + " ".join(map(str, a)))
    big = [_r.randint(-10**9, 10**9) for _ in range(2000)]
    cases.append(f"{big[100] + big[1900]} | " + " ".join(map(str, big)))
    return cases


def expected(line):
    """Brute force with the same rule as one pass: the first j that has a partner, and the
    latest index before j holding that partner."""
    t, rest = line.split("|")
    t, a = int(t), [int(x) for x in rest.split()]
    for j in range(len(a)):
        for i in range(j - 1, -1, -1):
            if a[i] + a[j] == t:
                return f"{i} {j}"
    return "none"
