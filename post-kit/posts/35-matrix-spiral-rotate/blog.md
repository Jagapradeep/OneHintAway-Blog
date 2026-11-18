Walking a grid in a fixed shape, or turning it in place? Two moves cover most of these problems. Worked examples: spiral order on the 3 × 4 grid 1 to 12, and a quarter turn of the 3 × 3 grid 1 to 9.

## The idea

**Spiral order.** Think of mowing a lawn from the outside in: along the top, down the right side, back along the bottom, up the left, then the next ring. Keep four walls, `top`, `bottom`, `left` and `right`. After each side is read, that wall moves one step in. After one lap of the 3 × 4 grid, `top` and `bottom` are both 1, `left` is 1 and `right` is 2, and the inner ring 6 7 is what's left.

The bottom row and the left side walk back the way you came. Before them, check that both a row and a column are still left: if `top > bottom` or `left > right`, everything has been read. Without that check, a single remaining row is read forwards and then backwards.

**Rotate right.** To turn a square grid a quarter to the right, swap every value across the top-left to bottom-right diagonal (`grid[i][j]` with `grid[j][i]`), then reverse each row. Both steps work inside the grid, so no second grid is needed.

## The walk

Spiral order of the 3 × 4 grid 1 2 3 4 / 5 6 7 8 / 9 10 11 12:

| Side | Reads | Wall after |
| --- | --- | --- |
| top row, left to right | 1 2 3 4 | top = 1 |
| right side, down | 8 12 | right = 2 |
| bottom row, right to left | 11 10 9 | bottom = 1 |
| left side, up | 5 | left = 1 |
| top row, left to right | 6 7 | top = 2 |

Result: {{sp(SPIRAL)}}. After the second top row, `top` is 2 and `bottom` is 1, so the check stops the walk.

Rotating 1 2 3 / 4 5 6 / 7 8 9: swapping across the diagonal gives 1 4 7 / 2 5 8 / 3 6 9, and reversing each row gives **7 4 1 / 8 5 2 / 9 6 3**.

Quick check: the spiral order of the 2 × 3 grid 1 2 3 / 4 5 6 is **{{sp(spiral_order([[1, 2, 3], [4, 5, 6]]))}}**.

## Pseudocode

`rotate` turns a square grid right; `spiralOrder` reads any grid in spiral order.

{{PSEUDOCODE}}

**The trap:** skip the `if top > bottom or left > right` check. On the 3 × 4 grid, the last lap leaves one row, 6 7, and the bottom pass walks it again: the result ends 5 6 7 6 instead of 5 6 7.

{{CODE}}

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Spiral | O(m · n) time | Each cell is read once |
| Rotate | O(n²) time | Each cell is swapped about twice |
| Extra space | O(1) | Both work inside the grid; the spiral only adds its result list |

## How it was tested

{{TESTED}}
