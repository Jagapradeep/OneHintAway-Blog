Clues: **the array is sorted** and **you need a pair** with some property, such as a target sum. Worked example: **LeetCode 167, Two Sum II - Input Array Is Sorted** (Medium).

## The walk

`numbers = [1, 3, 4, 6, 8, 11]`, `target = 10` returns `[{{ANSWER[0]}}, {{ANSWER[1]}}]` (positions of 4 and 6, counted from 1).

| left | right | sum | move |
|------|-------|-----|------|
| 1 | 11 | 12 | too big: right in |
| 1 | 8 | 9 | too small: left in |
| 3 | 8 | 11 | too big: right in |
| 3 | 6 | 9 | too small: left in |
| 4 | 6 | 10 | found it |

{{CHECKS}} checks instead of {{PAIRS}} pairs.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** two pointers only works on sorted input. On `[1, 4, 6, 3]` with target 10, every sum is too small and nothing is found, even though 4 + 6 = 10. Sort first, or use the hash map from post 05.

{{CODE}}

## Complexity

| Version | Time | Extra space |
|---|---|---|
| Every pair | O(n²) | O(1) |
| Hash map (post 05) | O(n) | O(n) |
| Two pointers | O(n) | O(1) |

## How it was tested

{{TESTED}}
