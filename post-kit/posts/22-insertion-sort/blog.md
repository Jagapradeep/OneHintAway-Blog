Small or almost-sorted input? Sort it like a hand of cards. Worked example: insertion sort on **5 2 4 1 3**.

## The idea

You pick up cards one at a time, and each new card slides left past every bigger card, so the cards in your hand stay sorted. That hand is the sorted part, and it grows by one card each pass.

In the array, picking up the card leaves a gap. Each bigger value to its left shifts one place right, so the gap walks left. When the value on the left is smaller, or the gap reaches the front, the card drops into the gap.

Each shift fixes one pair of values that was out of order. So the work grows with how unsorted the input is:

| Input | | Shifts |
| --- | --- | --- |
| 1 2 3 4 5 | sorted | 0 |
| 1 2 4 3 5 | one pair swapped | 1 |
| 5 4 3 2 1 | reversed | 10 |

## The walk

Insertion sort on 5 2 4 1 3:

| Pass | Card | Bigger values shifted | Card lands at index | Array after |
| --- | --- | --- | --- | --- |
| start | | | | 5 2 4 1 3 |
| 1 | 2 | 5 | 0 | 2 5 4 1 3 |
| 2 | 4 | 5 (2 stops it) | 1 | 2 4 5 1 3 |
| 3 | 1 | 5, 4, 2 | 0 | 1 2 4 5 3 |
| 4 | 3 | 5, 4 (2 stops it) | 2 | 1 2 3 4 5 |

Four passes and {{SHIFTS}} shifts in all.

Quick check: insertion sort on 4 3 2 1 makes **6 shifts**. The 3 makes 1, the 2 makes 2 and the 1 makes 3.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** skip line 3 and use `nums[i]` in lines 5 and 8 instead of a saved `card`. Line 6 writes over `nums[i]`, so the card is lost: the first shift copies 5 over the 2, and 5 2 4 1 3 comes out as 5 5 5 5 5. With the card saved first, it comes out as 1 2 3 4 5.

{{CODE}}

## Complexity

| | Time | Why |
| --- | --- | --- |
| Worst case (reversed) | O(n²) | n(n − 1)/2 shifts |
| Sorted input | O(n) | n − 1 compares, no shifts |
| Extra space | O(1) | It sorts inside the array |

## How it was tested

{{TESTED}}
