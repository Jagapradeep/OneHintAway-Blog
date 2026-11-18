Does a path of touching cells spell a word, using each cell once? Mark, explore, unmark. Worked example: **CAT** in the grid C A T / A R T (LeetCode 79).

## The idea

A board of letter tiles. Spell CAT by stepping from tile to a tile that touches it, up, down, left or right, never standing on the same tile twice. If a path runs out, step back and try another way.

That is backtracking from [post 38](/posts/backtracking-template/) on a grid. The choice is which neighbouring tile to step on next:

1. **Check** that the tile holds the letter we need, `word[i]`.
2. **Mark** it with `#` while we stand on it, so the path can't use it again.
3. **Explore** every tile next to it (down, up, right, left, inside the grid) for the next letter.
4. **Unmark** it on the way back, giving the tile its letter again so other paths can use it.

`exist` tries every tile as the first letter; `walk` does the rest.

## The walk

Finding CAT in C A T / A R T, trying down, up, right and left in that order:

| Step | Tile | Needs | Result |
| --- | --- | --- | --- |
| 1 | C at row 0, col 0 | C | match, mark it |
| 2 | A at row 1, col 0 (down) | A | match, mark it |
| 3 | its neighbours: # above, R right | T | no T: unmark the A, step back |
| 4 | A at row 0, col 1 (right of C) | A | match, mark it |
| 5 | T at row 0, col 2 | T | last letter: **{{tf(exist(GRID, 'CAT'))}}** |

Quick check: TRAC can be spelled too (**{{tf(exist(GRID, 'TRAC'))}}**): T at row 1, col 2, then R, then either A, then C.

## Pseudocode

`walk` checks one tile and explores from it; `exist` tries every starting tile.

{{PSEUDOCODE}}

**The trap:** skip line 6, the mark. Then `walk` can step back onto the tile it came from: in this grid, CAC is "found" (C, A, then the same C) and `exist` returns {{tf(wrong_exist(GRID, 'CAC'))}}, although there is only one C. With the mark it returns {{tf(exist(GRID, 'CAC'))}}.

{{CODE}}

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Time | O(m · n · 3ᴸ) | From each of the m · n tiles, at most 3 new directions per letter; L = word length |
| Call depth | O(L) | One call per letter |
| Extra space | O(1) | The `#` mark replaces a separate grid of seen tiles |

## How it was tested

{{TESTED}}
