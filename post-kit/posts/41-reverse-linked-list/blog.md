Asked to reverse a linked list, or part of one, without building a new list? Turn every arrow around in one pass. Worked example: reversing **1 → 2 → 3 → 4 → 5** (LeetCode 206).

## The idea

People stand in a line, each with a hand on the shoulder of the person in front. To make the line face the other way, each person moves their hand to the person behind them. But before letting go, they must note who was in front, or the rest of the line is lost.

In a linked list each node's `next` arrow points to the node in front. Walk the list with two pointers: `prev`, the part already turned around (it starts as none), and `curr`, the node being turned. For each node:

1. Save the rest of the list: `rest = curr.next`.
2. Turn the arrow back: `curr.next = prev`.
3. Move both pointers one step: `prev = curr`, `curr = rest`.

Midway, the list is in two pieces: `prev` holds the reversed part and `curr` holds the part still to do. When `curr` reaches none, `prev` is on the old last node, which is the new head.

Copying the values into a stack and popping them also reverses the list, but needs O(n) extra space. Turning the arrows reuses the nodes you already have.

## The walk

Reversing 1 → 2 → 3 → 4 → 5:

| Loop | curr | rest saved | Arrow turned | prev after |
| --- | --- | --- | --- | --- |
| 1 | 1 | 2 | 1 → none | 1 |
| 2 | 2 | 3 | 2 → 1 | 2 |
| 3 | 3 | 4 | 3 → 2 | 3 |
| 4 | 4 | 5 | 4 → 3 | 4 |
| 5 | 5 | none | 5 → 4 | 5 |

`curr` is now none, and reading from `prev` gives **{{sp(REVERSED)}}**.

Quick check: after 3 loops, `prev` and `curr` hold **{{after_loops(LIST, 3)}}**.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** skip line 5 and move with `curr = curr.next` after turning the arrow. By then `curr.next` is `prev`, which is none on the first step, so the walk stops: after node 1, `curr` becomes none, and the result is just {{sp(WRONG)}} instead of {{sp(REVERSED)}}. The other four nodes are lost.

{{CODE}}

LeetCode provides the `ListNode` class; the C++ block shows its definition so the code compiles on its own.

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Time | O(n) | Each node is visited once and each arrow turned once |
| Extra space | O(1) | Three pointers |
| Copy into a stack | O(n) space | The easier way it replaces |

## How it was tested

{{TESTED}}
