Too many values for an O(n²) sort? Split the array in half, sort each half, and merge the two sorted halves. Worked example: merge sort on **5 2 4 6 1 3**.

## The idea

Two teachers each hold a pile of test papers, sorted by roll number. To make one sorted pile, you only ever look at the two top papers and take the smaller one. That is the merge: two fronts, one compare, one move, repeated until one pile runs out. Whatever is left in the other pile is already sorted, so it goes on the end as it is.

Merge sort turns any array into two sorted piles by calling itself (post 21 covers how that works): split the array in half, sort each half the same way, then merge. A piece with one value is already sorted, so the splitting stops there.

## The walk

Merge sort on 5 2 4 6 1 3. The splits go down to single values, then the merges come back up:

| Merge | Left | Right | Result |
| --- | --- | --- | --- |
| 1 | 2 | 4 | 2 4 |
| 2 | 5 | 2 4 | 2 4 5 |
| 3 | 1 | 3 | 1 3 |
| 4 | 6 | 1 3 | 1 3 6 |
| 5 | 2 4 5 | 1 3 6 | 1 2 3 4 5 6 |

{{MERGES}} merges in all. In the last one, 1 comes from the right, 2 from the left, 3 from the right, then 4 and 5 from the left, and the leftover 6 goes on the end.

Quick check: merging 1 4 with 2 3 takes **{{merge_compares([1, 4], [2, 3])}} compares** (1 vs 2, 4 vs 2, 4 vs 3). Then 4 is added without a compare.

## Pseudocode

The merge, as on the slides. `mergeSort` itself returns arrays of one value as they are, otherwise sorts the half before `middle` and the rest with itself and returns `merge(left, right)`; it is in full in the code below.

{{PSEUDOCODE}}

**The trap:** the loop stops as soon as one list runs out. Return only `result` and the other list's values are lost: merging 2 4 5 with 1 3 6 gives {{sp(wrong_merge([2, 4, 5], [1, 3, 6]))}}, without the 6. Add the rest of both lists and it gives {{sp(merge([2, 4, 5], [1, 3, 6]))}}.

{{CODE}}

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Time, every input | O(n log n) | About log n levels of halving, and each level merges all n values once |
| Extra space | O(n) | The merged lists |

The O(n²) sorts from [post 22](/posts/insertion-sort/), [post 23](/posts/selection-sort/) and [post 24](/posts/bubble-sort/) do about 1.25 billion steps on 50,000 values; merge sort does under a million.

## How it was tested

{{TESTED}}
