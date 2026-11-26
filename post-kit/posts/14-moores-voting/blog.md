Clue: **find the value that appears more than half the time**, with O(1) extra space. Worked example: **LeetCode 169, Majority Element** (Easy).

## The walk

`nums = [2, 1, 1, 3, 1]`. Answer: `{{ANSWER}}`.

| x | candidate | count |
|---|---|---|
| 2 | 2 (new) | 1 |
| 1 | 2 | 0 (cancel) |
| 1 | 1 (new) | 1 |
| 3 | 1 | 0 (cancel) |
| 1 | 1 (new) | 1 |

## Pseudocode

{{PSEUDOCODE}}

**The trap:** no majority? You still get a candidate. `[1, 2, 3]` returns {{majority_element(NOMAJ)}}, which appears once. When a majority isn't promised, count the candidate again and keep it only if it appears more than `floor(length(nums) / 2)` times.

{{CODE}}

## Complexity

| Version | Time | Extra space |
|---|---|---|
| Hash map count | O(n) | O(n) |
| Moore's voting | O(n) | O(1) |

## How it was tested

{{TESTED}}
