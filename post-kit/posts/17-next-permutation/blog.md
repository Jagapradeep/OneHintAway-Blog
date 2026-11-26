**LeetCode 31, Next Permutation** (Medium). Rearrange the array into the next bigger order, in place, with constant extra memory. If it is already the biggest order, wrap to the smallest. Example: `[1, 3, 5, 4, 2]` → `[{{', '.join(map(str, ANSWER))}}]`. Edge case: `[3, 2, 1]` → `[{{', '.join(map(str, EDGE))}}]`.

## The idea

From the right, `5 4 2` falls, so that tail is already its biggest order. The pivot is the first number from the right that is smaller than its neighbour: `3`. Its partner is the first number from the right that is bigger than it: `4`. Swap them (`1 4 5 3 2`), then reverse the tail into its smallest order: `1 4 2 3 5`.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** stopping after the swap. The tail still falls, so it is in its biggest order: `[1, 3, 5, 4, 2]` becomes `[{{', '.join(map(str, WRONG))}}]`, bigger but not the next one.

{{CODE}}

## Complexity

| Version | Time | Extra space |
|---|---|---|
| List every order | O(n · n!) | O(n!) |
| Pivot, swap, reverse | O(n) | O(1) |

## How it was tested

{{TESTED}}
