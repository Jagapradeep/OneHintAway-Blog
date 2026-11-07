Sorted array and one value to find? Check the middle and throw away the half that can't hold it. Worked example: find **7** in **1 3 5 7 9 11**.

## The idea

A friend picks a number from 1 to 100 and says "higher" or "lower" after each guess. Guess 50, and half the numbers are gone in one go. Guess the middle of what is left, and half of that goes too. That only works because the numbers are in order.

In the array, `low` and `high` fence the part that can still hold the target. Check the value in the middle:

- equal to the target: done, return the middle index;
- smaller: the target can only be to the right, so `low = middle + 1`;
- bigger: the target can only be to the left, so `high = middle - 1`.

If `low` passes `high`, nothing is left to check and the target isn't there.

## The walk

Find 7 in 1 3 5 7 9 11:

| low | high | middle | nums[middle] | Move |
| --- | --- | --- | --- | --- |
| 0 | 5 | 2 | 5 | 5 is less than 7: low = 3 |
| 3 | 5 | 4 | 9 | 9 is more than 7: high = 3 |
| 3 | 3 | 3 | 7 | found: return {{FOUND}} |

{{CHECKS}} checks. A one-by-one scan needs {{FOUND + 1}} here, and the gap grows fast: 1,000,000 sorted values need at most {{MAX_CHECKS}} checks.

Quick check: searching for 4 checks **{{checks(EXAMPLE, 4)}} middles** (5, 1, 3) before `low` passes `high` and it returns -1.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** loop while `low < high` and the loop stops as soon as one value is left, without checking it. Searching 1 3 5 7 9 11 for 11 returns {{wrong_search(EXAMPLE, 11)}}. With `low <= high` the last value gets its check and the answer is {{binary_search(EXAMPLE, 11)}}.

{{CODE}}

The code computes the middle as `low + (high - low) / 2`. It is the same index as `floor((low + high) / 2)`, but `low + high` can overflow a 32-bit integer on huge arrays, and this form can't.

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Time | O(log n) | Each check halves the range |
| Extra space | O(1) | Three numbers |
| One-by-one scan | O(n) | The slow way it replaces |

## How it was tested

{{TESTED}}
