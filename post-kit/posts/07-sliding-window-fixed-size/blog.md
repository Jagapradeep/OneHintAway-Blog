Clues: **numbers next to each other** (a subarray or substring) and **a fixed length k**. Worked example: **the biggest sum of k numbers in a row**, the GeeksforGeeks problem "Max Sum Subarray of size K".

## The walk

`nums = [2, 1, 5, 1, 3, 2]`, `k = 3` returns `{{BEST}}`.

| window | in | out | sum |
|---|---|---|---|
| [2, 1, 5] | first window | | 8 |
| [1, 5, 1] | 1 | 2 | 7 |
| [5, 1, 3] | 3 | 1 | **9** |
| [1, 3, 2] | 2 | 5 | 6 |

**Who leaves?** When `nums[i]` joins, `nums[i - k]` leaves. At `i = 3`, index `3 - 3 = 0` drops out, so the window stays exactly `k` long.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** subtract `nums[i - k + 1]` by mistake and at `i = 3` you remove the 1 that is still inside the window. The sums come out 8, 8, 6, 7 and you return 8 instead of 9.

{{CODE}}

## Complexity

| Version | Time | Extra space |
|---|---|---|
| Re-add every window | O(n·k) | O(1) |
| Sliding window | O(n) | O(1) |

## How it was tested

{{TESTED}}
