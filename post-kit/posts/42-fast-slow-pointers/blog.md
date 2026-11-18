Need a linked list's middle, or to know whether it loops, without extra memory? Send two pointers at different speeds. Worked examples: the list **1 to 6** with 6 linking back to 3 (LeetCode 141), and the same list without the loop (LeetCode 876).

## The idea

Two friends run, one twice as fast as the other. On a straight road the fast one simply reaches the end first. On a round track, the fast one comes up behind the slow one and catches them.

In a list, `slow` moves one node per round and `fast` moves two:

- **No loop:** `fast` reaches the end. It has gone twice as far as `slow`, so `slow` is in the middle. With an even number of nodes there are two middles, and this finds the second, as LeetCode 876 asks.
- **A loop:** `fast` never reaches the end. Once both are inside the loop, `fast` gains one node per round, so it can't jump over `slow`: they land on the same node within one lap.

The check compares nodes, not values: two different nodes can hold the same value.

## The walk

1 → 2 → 3 → 4 → 5 → 6, with 6 linking back to 3:

| Round | slow | fast | |
| --- | --- | --- | --- |
| start | 1 | 1 | |
| 1 | 2 | 3 | |
| 2 | 3 | 5 | |
| 3 | 4 | 3 | fast runs 6 → 3, back into the loop |
| 4 | 5 | 5 | they meet: a loop |

They meet on node **{{MEET}}** after {{ROUNDS}} rounds.

Quick check: on the same nodes with no loop, `fast` runs out when `slow` is on node **{{MIDDLE}}**, the middle.

## Pseudocode

`middleNode` stops when `fast` runs out; `hasCycle` stops early if the two meet.

{{PSEUDOCODE}}

**The trap:** check only `fast.next != none` in the loop condition. On an even-length list with no loop, such as 1 to 6, `fast` jumps from 5 to none, and the next check reads `next` of none: the program crashes ({{wrong_has_cycle(build(LIST)[0])}} in our test) instead of returning {{tf(has_cycle(build(LIST)[0]))}}. Check `fast != none` first.

{{CODE}}

LeetCode provides the `ListNode` class; the C++ block shows its definition so the code compiles on its own.

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Time | O(n) | Fast reaches the end, or meets slow within one lap of the loop |
| Extra space | O(1) | Two pointers |
| Set of seen nodes | O(n) space | The simpler way it replaces |

## How it was tested

{{TESTED}}
