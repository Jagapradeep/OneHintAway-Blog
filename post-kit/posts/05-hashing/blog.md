A hash map does two jobs. See "how many times does it appear?": **count**. See "have I seen this before?": **remember**. Worked example: **LeetCode 1, Two Sum** (Easy).

## The walk

`nums = [3, 8, 4, 6, 1]`, `target = 10` returns `[{{ANSWER[0]}}, {{ANSWER[1]}}]` (4 + 6).

| i | num | need | seen it? |
|---|-----|------|----------|
| 0 | 3 | 7 | no |
| 1 | 8 | 2 | no |
| 2 | 4 | 6 | no |
| 3 | 6 | 4 | yes, at index 2 |

{{LOOKS}} looks instead of up to {{PAIRS}} pairs.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** store the number before checking and it can pair with itself. For `nums = [3, 2, 4]`, `target = 6`, "store, then check" returns `[0, 0]`. "Check, then store" returns the correct `[1, 2]`.

{{CODE}}

## Complexity

| | Time | Space |
| --- | --- | --- |
| One pass with a map | O(n) | O(n) |
| Every pair | O(n²) | O(1) |

## How it was tested

{{TESTED}}
