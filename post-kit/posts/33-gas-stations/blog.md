Asked to make the largest gap as small as possible? Guess the gap and binary search it, even when it is a real number. Worked example: **GFG, Minimize Max Distance to Gas Station** (Hard; LeetCode 774 is the same problem, for premium members).

## The idea

A highway has petrol pumps at km 1, 3, 12 and 16, so the gaps between neighbouring pumps are 2, 9 and 4 km. You may build 3 more pumps. Where should they go so the longest drive between two pumps is as short as possible?

1. **Try every share.** Give each gap some of the new pumps and space them evenly inside it. Putting all 3 in the 9 km gap leaves a longest gap of 4 (the 4 km gap is untouched); one pump per gap leaves 4.5; two in the 9 and one in the 4 leaves 3. That works for 3 pumps, but with k up to 100,000 there are far too many shares to try.
2. **Guess the answer instead.** Pick a longest gap `d` and count how many pumps it needs. For the gaps 2, 9 and 4: `d` = 4.5 needs 1 pump, `d` = 3 needs 3, and `d` = 2 needs 5. A smaller `d` never needs fewer pumps, so the guesses that fit form one run.
3. **Binary search on d.** This is the search on answers from [post 32](/posts/binary-search-on-answers/), on real numbers. If `d` fits, try smaller; if it needs too many pumps, go bigger. Like tuning an old radio dial, each turn is half the last.
4. **Count, then stop.** A gap `g` needs `ceil(g / d) − 1` pumps: it is cut into `ceil(g / d)` pieces. `d` fits when the total is at most k. Because `d` is a real number, `low` and `high` never meet: stop when `high − low` is below 0.000001. Start with `high` = the whole road, a `d` that needs no pumps at all.

## The walk

Gaps 2, 9 and 4 with k = 3, starting from low = 0 and high = 15:

| Range | Try d | Pumps needed | Result |
| --- | --- | --- | --- |
| 0 to 15 | 7.5 | 0 + 1 + 0 = 1 | fits: high = 7.5 |
| 0 to 7.5 | 3.75 | 0 + 2 + 1 = 3 | fits: high = 3.75 |
| 0 to 3.75 | 1.875 | 1 + 4 + 2 = 7 | too many: low = 1.875 |
| 1.875 to 3.75 | 2.8125 | 0 + 3 + 1 = 4 | too many: low = 2.8125 |
| 2.8125 to 3.75 | 3.28125 | 0 + 2 + 1 = 3 | fits: high = 3.28125 |

After {{ROUNDS}} rounds the range is narrower than 0.000001 and `high` is **{{ANSWER}}**. New pumps at km 6, 9 and 14 give it: the gaps become 2, 3, 3, 3, 2 and 2.

Quick check: with 5 new pumps, can the longest gap be 2? Yes: `d` = 2 needs exactly {{pumps_needed(STATIONS, 2)}} pumps (0 + 4 + 1).

## Pseudocode

`pumpsNeeded` counts the pumps one guess needs; `minMaxGap` binary searches the guess.

{{PSEUDOCODE}}

{{CODE}}

`pumpsNeeded` can return a very large count when `d` is tiny, so Java and C++ keep it in a 64-bit integer.

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Time | O(n log(L / ε)) | About 50 rounds for a road of 10⁹ and ε = 0.000001, each walking the n gaps |
| Extra space | O(1) | Only `low`, `high` and `d` |
| Hand out pumps one by one | O(k log n) | Fine for small k, slow for k = 100,000 with a heap of fractions |

## How it was tested

{{TESTED}}
