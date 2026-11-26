Clue: **overlapping ranges to combine**, such as bookings or time slots. Worked example: **LeetCode 56, Merge Intervals** (Medium).

## The walk

Bookings `[[5, 8], [1, 3], [8, 9], [6, 7], [2, 4]]`, sorted by start: `{{fmt(SORTED)}}`.

| next | last block | overlap? | blocks after |
|---|---|---|---|
| [1, 3] | | first | [1, 3] |
| [2, 4] | [1, 3] | 2 ≤ 3, yes | [1, 4] |
| [5, 8] | [1, 4] | 5 > 4, no | [1, 4], [5, 8] |
| [6, 7] | [5, 8] | 6 ≤ 8, yes | [1, 4], [5, 8] (end stays 8) |
| [8, 9] | [5, 8] | 8 ≤ 8, yes | {{fmt(MERGED)}} |

## Pseudocode

{{PSEUDOCODE}}

**The trap:** keep the max. Write `last[1] = end` instead of `max(last[1], end)` and `[6, 7]` inside `[5, 8]` drops the end to 7, so `[8, 9]` no longer joins: `{{fmt(WRONG)}}`.

{{CODE}}

## Complexity

| Version | Time | Space |
|---|---|---|
| Compare every pair | O(n²) | O(n) |
| Sort, then one pass | O(n log n) | O(n) |

## How it was tested

{{TESTED}}
