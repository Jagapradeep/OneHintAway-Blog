Grid sorted row after row, each row starting after the one above ends? Read it as one long sorted row and binary search that. Worked example: find **11** in the grid **1 3 5 / 7 9 11**.

## The idea

A building numbers its flats 0, 1, 2 and on, floor by floor, 3 flats a floor. One number gives you both the floor and the door: divide by 3 for the floor, and the remainder is the door. Flat 4 is on floor 1, door 1.

A sorted grid works the same way. Put row 1 after row 0 and the grid is one sorted row of `rows × cols` values. Index `i` of that long row lives at:

- row `floor(i / cols)`
- column `i mod cols`

So the search from [post 28](/posts/binary-search/) works unchanged: it only reads `cell(grid, middle)` instead of `nums[middle]`. Nothing is copied; the long row exists only in the index arithmetic.

## The walk

Find 11 in 1 3 5 / 7 9 11 (3 columns):

| low | high | middle | Row, column | Value | Move |
| --- | --- | --- | --- | --- | --- |
| 0 | 5 | 2 | row 0, column 2 | 5 | less than 11: low = 3 |
| 3 | 5 | 4 | row 1, column 1 | 9 | less than 11: low = 5 |
| 5 | 5 | 5 | row 1, column 2 | 11 | found: {{FOUND}} |

Quick check: in a grid with 4 columns, index 6 is **{{rc(6, 4)}}**: 6 divided by 4 is 1 with remainder 2.

## Pseudocode

`searchMatrix` is post 28's search over indexes 0 to `cells - 1`. `cell(grid, i)` sets `cols = length(grid[0])` and returns `grid[floor(i / cols)][i mod cols]`; it is in full in the code below.

{{PSEUDOCODE}}

**The trap:** mix up rows and columns in `cell` (`row = i mod rows`, `col = floor(i / rows)`) and the grid is read column by column: 1 7 3 9 5 11, which isn't sorted. Binary search on it misses values: searching for 7 returns {{tf(wrong_search(GRID, 7))}}. Dividing by the number of columns reads row after row and returns {{tf(search_matrix(GRID, 7))}}.

{{CODE}}

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Time | O(log(m·n)) | Binary search over m·n cells |
| Extra space | O(1) | Nothing is copied |
| Check every cell | O(m·n) | The slow way it replaces |

A 100 × 100 grid needs at most {{MAX_CHECKS}} checks.

## How it was tested

{{TESTED}}
