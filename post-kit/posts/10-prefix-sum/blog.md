Clue: **many questions that ask "what is the sum from index left to right?"** on an array that never changes. Worked example: **LeetCode 303, Range Sum Query - Immutable** (Easy).

## The walk

`nums = [3, 1, 4, 1, 5]` gives `prefix = [{{', '.join(map(str, PREFIX))}}]`. Then the sum from index 1 to 3 is `prefix[4] - prefix[1]` = {{Q1}}, and from 2 to 4 it is {{Q2}}.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** forgetting the shift. `prefix[right] - prefix[left]` on the example gives {{WRONG}}, which drops `nums[3]`. Use `prefix[right + 1]`.

{{CODE}}

## Complexity

| Version | Build | Each query | Extra space |
|---|---|---|---|
| Add the numbers up per query | none | O(n) | O(1) |
| Prefix array | O(n) | O(1) | O(n) |

## How it was tested

{{TESTED}}
