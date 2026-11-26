Clues: **the longest stretch in a row** (a subarray or substring) and **a rule it must follow**, like "the sum is at most 5". Post 07's window never changed size. This one stretches and shrinks, like an inchworm.

## The walk

Daily costs `nums = [2, 1, 3, 1, 4]` with `budget = 5`.

| right | joins | total | shrink | window | length |
|---|---|---|---|---|---|
| 0 | 2 | 2 | | [2] | 1 |
| 1 | 1 | 2 + 1 = 3 | | [2, 1] | 2 |
| 2 | 3 | 3 + 3 = 6, too much | drop 2 → 4 | [1, 3] | 2 |
| 3 | 1 | 4 + 1 = 5 | | [1, 3, 1] | **3** |
| 4 | 4 | 5 + 4 = 9, too much | drop 1, drop 3 → 5 | [1, 4] | 2 |

Longest run: {{BEST}} days.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** measuring too early. Record the length before you shrink and you count a window that breaks the rule: "measure, then shrink" counts `1 + 3 + 1 + 4 = 9` as length 4. "Shrink, then measure" returns 3.

{{CODE}}

## Complexity

| Version | Time | Extra space |
|---|---|---|
| Try every stretch | O(n²) | O(1) |
| Grow and shrink | O(n) | O(1) |

## How it was tested

{{TESTED}}
