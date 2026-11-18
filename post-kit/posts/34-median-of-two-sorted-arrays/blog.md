Need the middle of two sorted arrays without merging them? Binary search where to cut the shorter one. Worked example: **LeetCode 4, Median of Two Sorted Arrays** (Hard).

## The idea

Two classes stand in queues, each sorted by height: 1 4 7 and 2 3 6 9. We want the middle height of all seven kids without forming one big queue.

1. **Merge, then pick.** Merge the two rows as in [post 25](/posts/merge-sort/): {{sp(MERGED)}}. The middle value is {{ANSWER}}. Correct, but O(m + n), and the problem asks for O(log(m + n)).
2. **Fill the left half.** The median splits all 7 values into a left half of {{HALF}} and a right half of 3. If the top row gives `i` values to the left half, the bottom row must give `half − i`. So the only real choice is `i`.
3. **Search the cut.** Binary search `i` from 0 to the length of the shorter row. Like sliding the divider on a shelf with two rows of books: too far one way, move it back, each move half the last.
4. **When the cut is right.** Every left value must be at most every right value. Check the bottom row's left edge `b[half − i − 1]` against the top row's right edge `a[i]`. If the bottom's edge is bigger, the top gave too few: `low = i + 1`. Otherwise `high = i`. This is lower bound from [post 29](/posts/lower-upper-bound/): find the first cut where the check passes. At that cut the other pair of edges is in order too.
5. **Read the median.** With an odd total, the median is the bigger of the two left edges. With an even total, it is the average of the bigger left edge and the smaller right edge. An edge past the end of a row counts as −∞ on the left and +∞ on the right. Search the shorter row, so `half − i` always lands inside the longer one.

## The walk

Top row 1 4 7, bottom row 2 3 6 9, so `half` = {{HALF}}, `low` = 0 and `high` = 3:

| Try i | Bottom gives | Bottom left edge | Top right edge | Result |
| --- | --- | --- | --- | --- |
| 1 | 3 | 6 | 4 | 6 > 4: low = 2 |
| 2 | 2 | 3 | 7 | 3 ≤ 7: high = 2 |

The cut takes 1 4 from the top and 2 3 from the bottom. The other edges are in order too (4 ≤ 6). Seven values is odd, so the median is max(4, 3) = **{{ANSWER}}**.

Quick check: if the top row gives 1 value to the left half, the bottom gives **{{HALF - 1}}**, because the left half always holds {{HALF}} values.

## Pseudocode

`edge` reads a row safely; `median` searches the cut in the shorter row and reads the answer from the edges.

{{PSEUDOCODE}}

**The trap:** averaging the two middle values with whole-number division. In Java and C++, `(leftMax + rightMin) / 2` on two `int`s drops the half: for [1, 2] and [3, 4] it gives {{int_average([1, 2], [3, 4])}} instead of {{show(median([1, 2], [3, 4]))}}. Divide by 2.0, or turn one side into a `double` first, as the code below does.

{{CODE}}

In Java and C++ the missing edges use the smallest and largest 32-bit integers, which are safely outside the −10⁶ to 10⁶ range of the values.

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Time | O(log(min(m, n))) | Binary search over the shorter row |
| Extra space | O(1) | A few numbers |
| Merge, then pick | O(m + n) | The slow way it replaces |

## How it was tested

{{TESTED}}
