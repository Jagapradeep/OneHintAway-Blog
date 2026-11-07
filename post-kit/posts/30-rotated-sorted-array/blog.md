Sorted array that was cut once and swapped round? Compare the middle with the last value to know which side of the drop you're on. Worked example: the minimum of **4 5 6 1 2 3**.

## The idea

A sorted deck of cards is cut once: the top part goes to the bottom. Now it rises, drops once, and rises again. The smallest card sits right after the drop, so finding the drop finds the minimum.

The last value is the key. Every value before the drop is bigger than the last value; every value from the drop on is not. So one compare tells you where the middle stands:

- `nums[middle] > nums[high]`: the middle is before the drop, so the minimum is to its right: `low = middle + 1`.
- otherwise: the middle is at or after the drop, so the minimum is the middle or to its left: `high = middle`.

The same trick searches for a target (LeetCode 33): any middle splits the range into two halves and at least one of them is sorted. If `nums[low] <= nums[middle]` the left half is sorted; check whether the target fits between its ends, and search that half or the other.

## The walk

Minimum of 4 5 6 1 2 3:

| low | high | middle | nums[middle] vs nums[high] | Move |
| --- | --- | --- | --- | --- |
| 0 | 5 | 2 | 6 vs 3: bigger | low = 3 |
| 3 | 5 | 4 | 2 vs 3: smaller | high = 4 |
| 3 | 4 | 3 | 1 vs 2: smaller | high = 3 |

`low` meets `high` at slot {{MIN_AT}}: the minimum is {{MIN}}.

Quick check: in 6 7 1 2 3 4 5 the minimum sits in **slot {{find_min_index([6, 7, 1, 2, 3, 4, 5])}}**, right after the drop from 7.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** compare the middle with `nums[low]` instead of `nums[high]`, and the compare can't tell "no drop" from "a drop on the right". On 4 5 6 1 2 3 it steps past the 1 and returns {{wrong_find_min(EXAMPLE)}}. Comparing with `nums[high]` returns {{MIN}}.

{{CODE}}

This needs distinct values, as in LeetCode 153. With repeats, `nums[middle] == nums[high]` can't pick a side.

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Time | O(log n) | Each compare halves the range |
| Extra space | O(1) | Three numbers |
| Scan for the minimum | O(n) | The slow way it replaces |

## How it was tested

{{TESTED}}
