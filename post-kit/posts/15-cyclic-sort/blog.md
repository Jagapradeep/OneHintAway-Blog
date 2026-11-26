Clue: **numbers from 0 to n** (or 1 to n) in an array of about n seats. Worked example: **LeetCode 268, Missing Number** (Easy).

## The walk

`[3, 0, 4, 1, 5]` becomes `[{{', '.join(map(str, AFTER))}}]` after {{SWAPS}} swaps and {{SKIPS}} skip. Seat 2 holds 5, not 2, so the answer is **{{ANSWER}}**.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** the number 5 has no seat. Check `seat < n` first. Without it, the code looks up `nums[5]` and crashes.

{{CODE}}

## Complexity

| Version | Time | Extra space |
|---|---|---|
| Sort, then scan | O(n log n) | O(1) |
| Cyclic sort | O(n) | O(1) |

## How it was tested

{{TESTED}}
