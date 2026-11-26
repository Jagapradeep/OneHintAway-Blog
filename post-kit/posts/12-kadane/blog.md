**LeetCode 53, Maximum Subarray** (Medium). Return the largest sum of a non-empty subarray (numbers in a row). Worked example: `nums = [-2, 3, -1, 4, -7, 5]` → `{{BEST}}` (the subarray `3 - 1 + 4`).

## The walk

| index | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| nums | -2 | 3 | -1 | 4 | -7 | 5 |
| current | -2 | 3 (fresh) | 2 | 6 | -1 | 5 (fresh) |
| best | -2 | 3 | 3 | 6 | 6 | 6 |

## Pseudocode

{{PSEUDOCODE}}

**The trap:** `best` starts at 0. A subarray needs at least one number. With `nums = [-3, -1, -2]`, starting `best` at 0 returns 0; starting it at `nums[0]` returns -1.

{{CODE}}

## Complexity

| Version | Time | Extra space |
|---|---|---|
| Every subarray | O(n²) | O(1) |
| Kadane | O(n) | O(1) |

## How it was tested

{{TESTED}}
