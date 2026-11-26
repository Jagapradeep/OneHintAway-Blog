**LeetCode 76, Minimum Window Substring (Hard).** Pattern: sliding window (post 08) + a counting map (post 05). Worked example: `s = "ABDBCA"`, `t = "ABC"` returns `"{{BEST}}"`. LeetCode's own example returns `"{{LEET}}"`.

## The walk

| step | move | letter | missing | window | recorded |
|---|---|---|---|---|---|
| 1 | grow | A | 2 | A | |
| 2 | grow | B | 1 | AB | |
| 3 | grow | D | 1 | ABD | |
| 4 | grow | B | 1 | ABDB | |
| 5 | grow | C | 0 | ABDBC | **ABDBC · 5** |
| 6 | shrink | A out | 1 | BDBC | |
| 7 | grow | A | 0 | BDBCA | 5, not shorter |
| 8 | shrink | B out | 0 | DBCA | **DBCA · 4** |
| 9 | shrink | D out | 0 | BCA | **BCA · 3** |
| 10 | shrink | B out | 1 | CA | |

## Pseudocode

{{PSEUDOCODE}}

**The trap:** lowering `missing` for every letter that joins. It should only drop when that letter was still needed (`need[c] > 0` before the decrement); otherwise the second B looks like progress. On the example, lowering it for every letter returns `"{{WRONG}}"` instead of `"{{BEST}}"`.

{{CODE}}

## Complexity

| Version | Time | Extra space |
|---|---|---|
| Try every stretch | O(m²) stretches, each checked letter by letter | O(k) |
| Grow and shrink | O(m + n) | O(k) |

## How it was tested

{{TESTED}}
