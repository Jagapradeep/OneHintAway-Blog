# Reference for post 32 (LeetCode 875). Every number on the slides and in the video comes from here.
import bisect


def hours_at(piles, speed):
    total = 0
    for pile in piles:
        total += -(-pile // speed)        # ceil(pile / speed)
    return total


def min_speed(piles, hours):
    low = 1
    high = max(piles)
    while low < high:
        speed = (low + high) // 2
        if hours_at(piles, speed) <= hours:
            high = speed
        else:
            low = speed + 1
    return low


def wrong_hours_at(piles, speed):
    """The trap: pile / speed rounded down."""
    return sum(pile // speed for pile in piles)


def wrong_min_speed(piles, hours):
    low, high = 1, max(piles)
    while low < high:
        speed = (low + high) // 2
        if wrong_hours_at(piles, speed) <= hours:
            high = speed
        else:
            low = speed + 1
    return low


def brute(piles, hours):
    m = max(piles)
    if m <= 5000:
        s = 1
        while hours_at(piles, s) > hours:
            s += 1
        return s
    return bisect.bisect_left(range(1, m + 1), True, key=lambda s: hours_at(piles, s) <= hours) + 1


PILES = [3, 6, 7, 11]
HOURS = 8
ANSWER = min_speed(PILES, HOURS)
SPEEDS = list(range(1, max(PILES) + 1))
PER_PILE = [-(-p // ANSWER) for p in PILES]


def video_steps(piles=PILES, hours=HOURS):
    low, high = 1, max(piles)
    steps = [{"frame": [low - 1, high - 1], "eq": ["hours allowed:", str(hours)],
              "caption": f"The answer is a speed from {low} to {high}. Test the middle one."}]
    while low < high:
        s = (low + high) // 2
        h = hours_at(piles, s)
        st = {"frame": [low - 1, high - 1], "gold": [s - 1], "chip": f"{s}: {h} h", "chip_hl": h <= hours}
        if h <= hours:
            st.update({"eq": [f"speed {s} → {h} h ≤ {hours}", "fast enough"],
                       "caption": f"Speed {s}: {h} hours, fast enough. high = {s}."})
            high = s
        else:
            st.update({"eq": [f"speed {s} → {h} h > {hours}", "too slow"],
                       "caption": f"Speed {s}: {h} hours, too slow. low = {s + 1}."})
            low = s + 1
        steps.append(st)
    return steps


# ---- video dressing: LOW / MID / HIGH labels, discarded side dimmed ----
def _dress(steps, n):
    for st in steps:
        fr = st.get("frame")
        if not fr:
            continue
        lo, hi = fr
        out = [i for i in range(n) if i < lo or i > hi]
        if out:
            st["dim"] = sorted(set(st.get("dim", []) + out))
        old = st.get("ptr") or {}
        ptr = {"low": old.get("low", lo)}
        if st.get("gold"):
            ptr["mid"] = st["gold"][0]
        ptr["high"] = old.get("high", hi)
        st["ptr"] = ptr
    return steps


def _narrow(steps):
    """After each check, a short step of its own: the range shrinks before the next middle appears."""
    out = []
    for k, st in enumerate(steps):
        out.append(st)
        nx = steps[k + 1] if k + 1 < len(steps) else None
        if not (nx and st.get("gold") and st.get("frame") and nx.get("frame")) or nx["frame"] == st["frame"]:
            continue
        (a, b), (c, d) = st["frame"], nx["frame"]
        if c < a or d > b:                  # a new search starts: not a shrink
            continue
        mid = {"frame": [c, d], "eq": st["eq"], "caption": st["caption"], "hold": 0.5}
        if st.get("steel") == [b]:
            mid["steel"] = [d]
        out.append(mid)
    return out


_raw_video_steps = video_steps


def video_steps(*args, **kw):
    return _dress(_narrow(_raw_video_steps(*args, **kw)), max(PILES))


# ---- tests for the four languages: one input per line, one answer per line ----
import random as _r


def test_inputs():
    _r.seed(32)
    cases = ["8|3 6 7 11", "5|30 11 23 4 20", "6|30 11 23 4 20", "1|1", "1|1000000000", "2|1000000000",
             "1000000000|1000000000", "4|5 5 5 5", "3|1 1 1", "10|7"]
    big = [_r.randint(1, 10**9) for _ in range(10000)]
    cases.append(f"{_r.randint(10000, 10**9)}|" + " ".join(map(str, big)))
    big2 = [10**9] * 10000
    cases.append("1000000000|" + " ".join(map(str, big2)))
    for _ in range(1200):
        n = _r.randint(1, 8)
        p = [_r.randint(1, 60) for _ in range(n)]
        cases.append(f"{_r.randint(n, n * 12)}|" + " ".join(map(str, p)))
    for _ in range(30):
        n = _r.randint(1, 6)
        p = [_r.randint(1, 10**9) for _ in range(n)]
        cases.append(f"{_r.randint(n, 10**9)}|" + " ".join(map(str, p)))
    return cases


def expected(line):
    h, rest = line.split("|")
    return str(brute([int(x) for x in rest.split()], int(h)))
