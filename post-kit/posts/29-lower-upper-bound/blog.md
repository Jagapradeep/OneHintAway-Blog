Values repeat and you need the first one, the last one, or how many there are? Find the first slot whose value is at least the target. Worked example: the 2s in **1 2 2 2 4 5**.

## The idea

A library shelf is sorted by book number, with three copies of book 2. Plain binary search ([post 28](/posts/binary-search/)) stops at whichever copy it meets first. Here we need the edges: the first copy, and the spot just after the last one.

`lowerBound(t)` returns the first slot whose value is at least `t`. Two changes from post 28 make it work:

- When the middle value is at least `t`, the middle might be the answer, so `high = middle` keeps it in range instead of skipping it.
- `high` starts at `length(nums)`, one past the end, so the answer can be "after everything" when every value is smaller than `t`.

For whole numbers, the spot just after the last `t` is the first value at least `t + 1`. So the upper bound is `lowerBound(t + 1)`, and the count of `t` is the difference.

## The walk

`lowerBound(2)` on 1 2 2 2 4 5:

| low | high | middle | nums[middle] | Move |
| --- | --- | --- | --- | --- |
| 0 | 6 | 3 | 2 | at least 2: high = 3 |
| 0 | 3 | 1 | 2 | at least 2: high = 1 |
| 0 | 1 | 0 | 1 | less than 2: low = 1 |

`low` meets `high` at {{LOWER}}. `lowerBound(3)` walks the same way to {{UPPER}}, so the 2s sit in slots {{LOWER}} to {{UPPER - 1}} and there are {{COUNT}} of them.

Quick check: `lowerBound(6)` is **{{lower_bound(EXAMPLE, 6)}}**, one past the end, because no value is 6 or more. That is why `high` starts at `length(nums)`.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** post 28's search returns as soon as it sees the target. On 1 2 2 2 4 5 it lands on the middle 2 and returns slot {{first_match_search(EXAMPLE, 2)}}. Lower bound keeps going left while it can and returns slot {{LOWER}}, the first 2.

{{CODE}}

The `target + 1` trick for the upper bound needs whole numbers whose `target + 1` doesn't overflow. For other values, copy the function and change `<` to `<=` on the comparison line: that version returns the first value strictly bigger than the target.

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Each bound | O(log n) | Each check halves the range |
| First, last and count of a value | O(log n) | Two bounds |
| Extra space | O(1) | Three numbers |

## How it was tested

{{TESTED}}
