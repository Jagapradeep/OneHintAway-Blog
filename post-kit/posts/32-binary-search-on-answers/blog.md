Asked for the smallest value that still works, and every bigger value works too? Binary search the answers instead of an array. Worked example: piles **3 6 7 11** in **8** hours (LeetCode 875's setup).

## The idea

Four piles of homework pages: 3, 6, 7 and 11. Each hour you read from one pile only, at a fixed speed, and a pile that runs out early still uses up the whole hour. You have 8 hours. How slowly can you read?

There is no sorted array here. But the possible answers, the speeds 1 to 11, are in order, and they split cleanly: slow speeds fail, and once one speed is fast enough, every faster speed is fast enough too. A row of "no, no, no, yes, yes, …" is exactly what lower bound ([post 29](/posts/lower-upper-bound/)) finds the first "yes" of.

So two pieces:

- **The check:** `hoursAt(piles, speed)` adds up `ceil(pile / speed)` for each pile. It answers "is this speed fast enough?" in O(n).
- **The search:** binary search the speeds from 1 to `max(piles)`. A speed faster than the biggest pile never helps, since each pile already takes one hour.

## The walk

Piles 3 6 7 11, 8 hours, speeds 1 to 11:

| low | high | speed | Hours at that speed | Move |
| --- | --- | --- | --- | --- |
| 1 | 11 | 6 | {{hours_at(PILES, 6)}} | fast enough: high = 6 |
| 1 | 6 | 3 | {{hours_at(PILES, 3)}} | too slow: low = 4 |
| 4 | 6 | 5 | {{hours_at(PILES, 5)}} | fast enough: high = 5 |
| 4 | 5 | 4 | {{hours_at(PILES, 4)}} | fast enough: high = 4 |

`low` meets `high` at {{ANSWER}}: speed {{ANSWER}} takes {{hours_at(PILES, ANSWER)}} hours ({{' + '.join(map(str, PER_PILE))}}), and speed {{ANSWER - 1}} takes {{hours_at(PILES, ANSWER - 1)}}.

Quick check: at speed 6 the piles take **{{hours_at(PILES, 6)}} hours**: 1 + 1 + 2 + 2.

## Pseudocode

`minSpeed` searches the speeds. Its check, `hoursAt(piles, speed)`, adds `ceil(pile / speed)` over every pile; it is in full in the code below.

{{PSEUDOCODE}}

**The trap:** `pile / speed` in whole numbers rounds down, so the last part-hour of each pile goes missing. Speed 3 then looks like it takes {{wrong_hours_at(PILES, 3)}} hours instead of {{hours_at(PILES, 3)}}, and the search returns {{wrong_min_speed(PILES, HOURS)}} instead of {{ANSWER}}. Round up: `ceil(pile / speed)`, which in whole numbers is `(pile + speed - 1) / speed`.

{{CODE}}

With 10,000 piles of up to 10⁹ pages, the total hours at speed 1 can pass the 32-bit limit, and so can `pile + speed - 1`. The Java and C++ versions use 64-bit integers for both.

## Complexity

| | Cost | Why |
| --- | --- | --- |
| Time | O(n log m) | log m speeds checked, each check walks n piles (m = the biggest pile) |
| Extra space | O(1) | A few numbers |
| Try every speed | O(n · m) | The slow way it replaces |

## How it was tested

{{TESTED}}
