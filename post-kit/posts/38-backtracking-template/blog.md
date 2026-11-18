Asked for every arrangement, or every combination that follows a rule? Choose, explore, undo. Worked examples: every order of **1 2 3** (LeetCode 46) and the combinations of **2 3 6 7** that add up to **7** (LeetCode 39).

## The idea

Three friends and three seats in a row. Seat someone in seat 1, then someone still standing in seat 2, then the last one in seat 3. Then stand the last one up and try someone else. Seat 1 has 3 choices, seat 2 has 2 and seat 3 has 1, so there are 3 × 2 × 1 = {{len(PERMS)}} orders.

That is the whole backtracking template, three moves repeated:

1. **Choose:** mark a value as used and add it to the path.
2. **Explore:** call the same function for the next step.
3. **Undo:** remove the value and mark it free again, then try the next one.

[Post 37](/posts/subsets/) used the same moves with two choices per value, pick or skip. Here the rule for what you may choose changes, and nothing else does.

**Combination sum** uses the same moves with a new rule: choose numbers that add up to the target, reusing any number. To stop the same numbers coming back in another order, the loop starts at `i`, and the recursive call passes `j`: the same number may come again, but never an earlier one.

## The walk

Every order of 1 2 3, in the order the code saves them:

| Seat 1 | Then | Saved |
| --- | --- | --- |
| 1 | 2, 3 | 1 2 3 |
| 1 | undo 3, undo 2, then 3, 2 | 1 3 2 |
| 2 | 1, 3 | 2 1 3 |
| 2 | 3, 1 | 2 3 1 |
| 3 | 1, 2 | 3 1 2 |
| 3 | 2, 1 | 3 2 1 |

Combination sum on 2 3 6 7 with target 7: 2 + 2 + 3 reaches 7, the other paths that start with 2 overshoot or run out, 3 + 3 needs a 1 that isn't there, 6 needs a 1 too, and 7 alone works. The result is {{show(COMBOS)}}.

Quick check: 4 friends have **{{len(perms([1, 2, 3, 4]))}}** orders, 4 × 3 × 2 × 1.

## Pseudocode

`permute` lists every order; `find` lists every combination that adds up to the target. Start them with `permute(nums, all false, empty, empty)` and `find(nums, 0, target, empty, empty)`.

{{PSEUDOCODE}}

**The trap:** pass `0` instead of `j` in the recursive call of `find`. Every order of the same numbers is then found again: {{show(wrong_combos(CANDS, TARGET))}} instead of {{show(COMBOS)}}.

{{CODE}}

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Permutations | O(n · n!) time | n! orders, each copied in n steps |
| Combination sum | O(n^(t/m)) time | t = target, m = the smallest number: the deepest path |
| Call depth | O(n) for permutations, O(t/m) for combinations | One call per seat or per number added |

## How it was tested

{{TESTED}}
