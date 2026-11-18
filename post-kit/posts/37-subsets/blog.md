Asked for every group you could choose from a small set? For each value, pick it, then skip it. Worked example: every subset of **1 2 3** (LeetCode 78).

## The idea

Three snacks are on the table. For each one you decide: into the lunchbox, or leave it out. One snack gives 2 lunchboxes, two give 2 × 2 = 4, and three give 2 × 2 × 2 = {{COUNT}}, the empty box included.

The code makes the same choices in order. At value `i`, it first **picks** it: add `nums[i]` to the `picked` list and decide the rest. Then it **skips** it: remove that last pick and decide the rest again. When every value has been decided, `picked` is one subset, and a copy of it is saved.

One list serves every subset because of the undo. Removing the last pick takes the list back to what it was, so the skip branch starts clean. This pick, explore, undo rhythm is backtracking, and the next posts build on it.

## The walk

Every subset of 1 2 3, in the order the code saves them:

| Choices | Saved |
| --- | --- |
| pick 1, pick 2, pick 3 | [1 2 3] |
| pick 1, pick 2, skip 3 | [1 2] |
| pick 1, skip 2, pick 3 | [1 3] |
| pick 1, skip 2, skip 3 | [1] |
| skip 1, pick 2, pick 3 | [2 3] |
| skip 1, pick 2, skip 3 | [2] |
| skip 1, skip 2, pick 3 | [3] |
| skip 1, skip 2, skip 3 | [] |

The first four pick 1; the last four are the same four without it.

Quick check: 1 2 3 4 has **{{len(subsets([1, 2, 3, 4]))}}** subsets. The 4 doubles the 8: each one with it, and without it.

## Pseudocode

`build` decides value `i` and recurses; `subsets` starts it with nothing picked.

{{PSEUDOCODE}}

**The trap:** write `add picked to out` on line 3, without the copy. Every saved entry is then the same list, and the undos empty it, so `subsets([1, 2, 3])` returns 8 empty lists instead of {{show(ALL)}}.

{{CODE}}

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Time | O(n · 2ⁿ) | 2ⁿ subsets, each copied in up to n steps |
| Call depth | O(n) | One call per value decided |
| Output | O(n · 2ⁿ) | The subsets themselves |

## How it was tested

{{TESTED}}
