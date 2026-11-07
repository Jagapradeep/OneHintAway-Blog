Only allowed to swap neighbours? Sweep the row and swap every pair that is out of order. Worked example: bubble sort on **5 2 4 1 3**.

## The idea

Kids stand in a line. Walk along it: whenever a taller kid stands just before a shorter one, they swap places. After one walk the tallest kid is at the back for good. Each walk is a sweep, and each sweep fixes one more spot at the end.

So sweep 1 compares every pair, sweep 2 can skip the last slot, sweep 3 the last two, and so on. If a whole sweep makes no swap, every pair is already in order and the sort can stop early.

## The walk

Bubble sort on 5 2 4 1 3:

| Sweep | Swaps in this sweep | Array after |
| --- | --- | --- |
| start | | 5 2 4 1 3 |
| 1 | 5↔2, 5↔4, 5↔1, 5↔3 | 2 4 1 3 5 |
| 2 | 4↔1, 4↔3 | 2 1 3 4 5 |
| 3 | 2↔1 | 1 2 3 4 5 |
| 4 | none, so it stops | 1 2 3 4 5 |

{{SWEEPS}} sweeps and {{SWAPS}} swaps in all.

Quick check: on 1 2 3 5 4, bubble sort with the early stop runs **{{sweeps([1, 2, 3, 5, 4])}} sweeps**. Sweep 1 swaps 5 and 4; sweep 2 swaps nothing and stops.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** indent the `if not swapped` check one level too far, inside the `for j` loop, and it runs after every pair instead of after the whole sweep. Sweep 2 sees 2 and 4 in order first and quits, so 5 2 4 1 3 comes out as {{sp(wrong_sort(EXAMPLE))}}. With the check after the sweep, it comes out as {{sp(bubble_sort(EXAMPLE))}}.

{{CODE}}

## Complexity

| | Time | Why |
| --- | --- | --- |
| Worst case (reversed) | O(n²) | n(n − 1)/2 swaps, one per out-of-order pair |
| Sorted input | O(n) | One sweep with no swap, then it stops |
| Extra space | O(1) | It sorts inside the array |

Bubble sort makes as many swaps as insertion sort ([post 22](/posts/insertion-sort/)) makes shifts: one per pair that is out of order.

## How it was tested

{{TESTED}}
