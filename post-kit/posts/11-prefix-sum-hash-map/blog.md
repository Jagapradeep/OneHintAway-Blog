**LeetCode 560, Subarray Sum Equals K** (Medium). Count the subarrays whose numbers add up to `k`. Numbers can be negative, which is why a sliding window does not work here.

## The walk

`nums = [1, -1, 3, 1, 2]`, `k = 3` → `{{COUNT}}`. Running sums, starting from the empty start: `{{', '.join(map(str, SUMS))}}`.

| sum now | earlier sum it needs | times seen | subarray |
|---|---|---|---|
| 3 | 0 | 2 (the empty start and after −1) | `[1, -1, 3]` and `[3]` |
| 4 | 1 | 1 | `[-1, 3, 1]` |
| 6 | 3 | 1 | `[1, 2]` |

## Pseudocode

{{PSEUDOCODE}}

**The trap:** the missing 0. A subarray that starts at index 0 needs an earlier sum of 0. Without `seen[0] = 1` the example returns {{WRONG}} and misses `[1, -1, 3]`.

{{CODE}}

## Complexity

| Version | Time | Extra space |
|---|---|---|
| Every subarray | O(n²) | O(1) |
| Running sums + map | O(n) | O(n) |

## How it was tested

{{TESTED}}
