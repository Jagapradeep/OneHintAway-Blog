**LeetCode 42, Trapping Rain Water** (Hard). Worked example: `height = [3, 0, 1, 4, 0, 2]` → `{{WATER}}`. Water above each bar: {{sp(LEVELS)}}.

## The idea

Water above a bar = the lower of the tallest walls on its two sides, minus the bar. Two walkers start at the ends. Whichever side is lower gets settled: the other side holds a bar at least as tall, so the lower side's own tallest wall is the limit.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** settling the taller side. The rule only works for the lower side. Swap the test and the example returns {{WRONG}} instead of {{WATER}}.

{{CODE}}

## Complexity

| Version | Time | Extra space |
|---|---|---|
| Scan both sides per bar | O(n²) | O(1) |
| Two arrays of tallest walls | O(n) | O(n) |
| Two walkers | O(n) | O(1) |

## How it was tested

{{TESTED}}
