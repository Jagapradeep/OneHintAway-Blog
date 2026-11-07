Counting pairs `i < j` where the left value is more than double the right? Merge sort can count them while it sorts. Worked example: **LeetCode 493, Reverse Pairs** (Hard).

## The idea

Kids stand in a line. A kid is a giant to anyone behind them who is less than half their height, and we count every giant pair. In array terms: count the pairs `i < j` with `nums[i] > 2 * nums[j]`. For [6, 4, 1, 5, 2] there are {{TOTAL}}: {{PAIRS}}.

1. **Check every pair.** It works, but it is n(n − 1)/2 checks: over a billion for 50,000 values.
2. **Sorted halves count fast.** Split the line in two. Every pair is either inside the left half, inside the right half, or across. If both halves are sorted, the pairs across line up: once a left value pairs with a right value r, every bigger left value pairs with r too.
3. **Merge sort does the sorting.** Merge sort ([post 25](/posts/merge-sort/)) already splits the line and hands back sorted halves just before each merge. Pairs inside a half are the same problem, smaller, so the function calls itself. Pairs across are counted, then the halves are merged.
4. **One walk across.** For each right value r, move a pointer `i` past the left values that are at most `2 * r`. Every left value from `i` to the end of the left half pairs with r. The right half is sorted, so r only grows and `i` never walks back: one walk per merge. `2 * r` can pass the 32-bit limit, so it is kept in 64 bits.

## The walk

On [6, 4, 1, 5, 2], counting across just before each merge:

| Left half | Right half | Pairs across | Running total |
| --- | --- | --- | --- |
| 6 | 4 | 0 | 0 |
| 4 6 | 1 | 2 (6 and 4 with 1) | 2 |
| 5 | 2 | 1 (5 with 2) | 3 |
| 1 4 6 | 2 5 | 1 (6 with 2) | {{TOTAL}} |

Quick check: with sorted halves 3 7 9 and 1 4, there are **{{cross([3, 7, 9], [1, 4])}} pairs across**: 1 pairs with 3, 7 and 9, and 4 pairs only with 9.

## Pseudocode

`reversePairs` starts the count; `countPairs` splits, counts inside each half, counts across, then merges.

{{PSEUDOCODE}}

**The trap:** `2 * nums[j]` overflows a 32-bit integer when `nums[j]` is near 2³¹ − 1 or −2³¹. Keep it in a 64-bit integer (`long` in Java, `long long` in C++). Python and JavaScript numbers are big enough here.

{{CODE}}

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Time | O(n log n) | About log n levels, and each level does one O(n) walk and one O(n) merge |
| Extra space | O(n) | The merge's buffer |
| Check every pair | O(n²) | The slow way it replaces |

## How it was tested

{{TESTED}}
