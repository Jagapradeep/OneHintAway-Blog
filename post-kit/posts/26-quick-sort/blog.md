Need the k-th smallest or largest value? Partition around a pivot and keep only the side that holds it. Worked example: quick sort and quickselect on **5 2 4 1 3**.

## The idea

Kids stand in a row. Pick the last kid as the pivot. Everyone shorter moves to the pivot's left, everyone taller to its right. Now the pivot stands exactly where it will be in the sorted row, even though neither side is sorted yet. That move is called partition.

In the array, a `wall` starts at the left end. Every value smaller than the pivot is swapped to the wall, and the wall moves one step right. At the end, the pivot swaps into the wall's slot: everything left of it is smaller, everything right of it is not.

- **Quick sort** partitions, then does the same on the left side and on the right side.
- **Quickselect** wants only the k-th smallest, which belongs in slot k − 1. After one partition it knows which side holds that slot, and it throws the other side away.

## The walk

Partition of 5 2 4 1 3 with pivot 3:

| j | Value | Smaller than 3? | Move | Array after | Wall |
| --- | --- | --- | --- | --- | --- |
| 0 | 5 | no | | 5 2 4 1 3 | 0 |
| 1 | 2 | yes | swap slots 0 and 1 | 2 5 4 1 3 | 1 |
| 2 | 4 | no | | 2 5 4 1 3 | 1 |
| 3 | 1 | yes | swap slots 1 and 3 | 2 1 4 5 3 | 2 |
| end | | | pivot into slot 2 | {{sp(AFTER)}} | |

3 is home in slot {{SPOT}}. Quick sort then partitions 2 1 (1 lands in slot 0) and 5 4 (4 lands in slot 3), and the row is {{sp(quick_sort(EXAMPLE))}}.

Quickselect for the 4th smallest: after the first partition the pivot is in slot 2, but the answer belongs in slot 3, so only 5 4 is kept. Partitioning 5 4 puts 4 in slot 3: the answer is {{quick_select(EXAMPLE, 4)}}, after {{select_rounds(EXAMPLE, 4)}} partitions.

Quick check: partitioning 3 5 1 2 4 (pivot 4) puts 4 in **slot {{spot_of([3, 5, 1, 2, 4])}}**, because three values are smaller than it.

## Pseudocode

Partition, as on the slides. `quickSort` calls it while `low < high`, then sorts `low` to `spot - 1` and `spot + 1` to `high`. `quickSelect` calls it in a loop: it returns `nums[spot]` when `spot == k - 1`, moves `low` past the spot when the spot is too small, and `high` below it otherwise. Both are in full in the code below.

{{PSEUDOCODE}}

**The trap:** `quickSelect` counts from the smallest. For the k-th largest, passing k straight in gives the k-th smallest: the 2nd largest of 5 2 4 1 3 comes out as {{wrong_kth_largest(EXAMPLE, 2)}}. Ask for the (n − k + 1)-th smallest instead, the 4th smallest here, and it comes out as {{kth_largest(EXAMPLE, 2)}}.

{{CODE}}

## Complexity

| | Average | Worst case |
| --- | --- | --- |
| Quick sort | O(n log n) | O(n²) |
| Quickselect | O(n) | O(n²) |
| Extra space | O(log n) call stack on average | O(n) |

The worst case comes from bad pivots, such as sorted input with the last value as pivot. Swapping a random value to the end before each partition makes that very unlikely. Many equal values are a second weak spot for this partition; the three-way split from post 13 handles them.

## How it was tested

{{TESTED}}
