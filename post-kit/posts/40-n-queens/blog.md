Place pieces so no two clash, and list every way? Fill one row at a time and back up when a row has no safe spot. Worked example: **LeetCode 51, N-Queens** (Hard), with n = 4.

## The idea

Four guests who all quarrel sit on a 4 × 4 floor of cushions. Any two in the same row, column or diagonal start a fight. In chess terms: place n queens on an n × n board so that no two attack each other, and return every such board.

1. **Try every board.** Choose any 4 of the 16 squares and check for attacks: {{f'{BOARDS_ALL:,}'}} boards for n = 4, and {{f'{BOARDS_8:,}'}} for n = 8. Most are hopeless after the second queen.
2. **One queen per row.** Two queens in the same row attack, so each row holds exactly one queen. The only choice left is its column.
3. **Back up and move.** This is the backtracking template from [post 38](/posts/backtracking-template/). Place a queen in row 0, then row 1, and so on. When a row has no safe column, the queen in the row above moves to its next safe column; if it has none, back up further. Like seating quarrelling guests row by row and reseating the last guest when nobody fits.
4. **The safe test.** Keep `queens[r]`, the column of the queen in row `r`. A new square `(row, col)` is attacked by that queen when `col == c` (same column) or `col == c ± (row − r)` (same diagonal), where `c = queens[r]`. Rows below are still empty, so only the rows above need checking.

## The walk

n = 4, trying columns from left to right:

| Step | What happens |
| --- | --- |
| 1 | row 0 → column 0 |
| 2 | row 1 → column 2 (0 and 1 are attacked) |
| 3 | row 2: every column attacked, back up |
| 4 | row 1 → column 3 |
| 5 | row 2 → column 1 |
| 6 | row 3: every column attacked; rows 2, 1 and 0 run out too |
| 7 | row 0 → column 1 |
| 8 | row 1 → column 3, row 2 → column 0, row 3 → column 2: **{{' '.join(map(str, FIRST))}}** |

The search goes on and finds the mirror image, 2 0 3 1. So n = 4 has **{{len(SOLS)}}** boards: `.Q.. ...Q Q... ..Q.` and `..Q. Q... ...Q .Q..`.

Quick check: with queens at row 0 column 0 and row 1 column 2, the safe columns in row 2 are: **{{safe_cols([0, 2], 2, 4)}}**. Columns 0 and 2 are taken, and 1 and 3 are on a diagonal.

## Pseudocode

`safe` tests one square against the rows above; `place` fills the rows one by one. Start it with `place(n zeros, 0, n, empty list)`. There is no separate undo line: trying the next column overwrites `queens[row]`.

{{PSEUDOCODE}}

{{CODE}}

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Time | O(n · n!) | At most n columns in row 0, fewer below, and an O(n) safe test each |
| Extra space | O(n) | `queens` and the call stack, besides the boards returned |
| Try every board | O(C(n², n) · n²) | The slow way it replaces |

## How it was tested

{{TESTED}}
