Want to sort with as few swaps as possible? Pick the smallest value each pass and swap it to the front. Worked example: selection sort on **5 2 4 1 3**.

## The idea

Kids wait in a row. Each round you call the shortest one still waiting, and they swap into the next spot at the front. The front of the row is the sorted part: it grows by one spot each round, and nobody in it moves again.

In the array, pass `i` scans the unsorted part (index `i` to the end) and remembers the **index** of the smallest value it has seen. Only when the scan is over does it swap that value into slot `i`. One swap per pass, so at most n − 1 swaps in all.

## The walk

Selection sort on 5 2 4 1 3:

| Pass | Unsorted part | Smallest | Move | Array after |
| --- | --- | --- | --- | --- |
| start | | | | 5 2 4 1 3 |
| 1 | 5 2 4 1 3 | 1 | swaps with 5 | 1 2 4 5 3 |
| 2 | 2 4 5 3 | 2 | already in place | 1 2 4 5 3 |
| 3 | 4 5 3 | 3 | swaps with 4 | 1 2 3 5 4 |
| 4 | 5 4 | 4 | swaps with 5 | 1 2 3 4 5 |

{{PASSES}} passes, {{COMPARES}} compares and only {{SWAPS}} swaps.

Quick check: selection sort on 4 3 2 1 makes **{{swaps([4, 3, 2, 1])}} swaps**. 1 trades with 4, 2 trades with 3, and 3 is already home.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** remember the smallest *value* (`smallest = nums[j]`) instead of its index, and all you can do at the end is copy it over `nums[i]` (`nums[i] = smallest`). The old `nums[i]` is lost: 5 2 4 1 3 comes out as {{sp(wrong_sort(EXAMPLE))}}. Remember the index and swap, and it comes out as {{sp(selection_sort(EXAMPLE))}}.

{{CODE}}

## Complexity

| | Time | Why |
| --- | --- | --- |
| Every input | O(n²) | n(n − 1)/2 compares, even when already sorted |
| Swaps | O(n) | At most one per pass |
| Extra space | O(1) | It sorts inside the array |

Compared with insertion sort ([post 22](/posts/insertion-sort/)), selection sort does not get faster on almost-sorted input, but it moves values far fewer times.

## How it was tested

{{TESTED}}
