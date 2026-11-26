Clue: **only three kinds of values** to group, in place. Worked example: **LeetCode 75, Sort Colors** (Medium): 0s first, then 1s, then 2s, in one pass. `nums = [1, 0, 2, 2, 1, 0]` → `[{{', '.join(map(str, SORTED))}}]` in {{STEPS}} steps.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** after swapping with `high`, do not move `mid`. The number that came back from `high` has not been checked yet. On `[1, 2, 0]`, moving `mid` there too returns `[{{', '.join(map(str, wrong_sort_colors(TRAP)))}}]`. Keep `mid` where it is and it checks that 0 next.

{{CODE}}

## Complexity

| Version | Time | Extra space |
|---|---|---|
| Count, then rewrite | O(n), two passes | O(1) |
| Three pointers | O(n), one pass | O(1) |

## How it was tested

{{TESTED}}
