The clue: a problem asks for x to the power n with a huge n, or says "answer mod 1,000,000,007". Worked example: `power(3, 13, 1000)`, the GeeksforGeeks problem "Modular Exponentiation for Large Numbers".

## The walk

| n | odd? | block mod 1000 | answer mod 1000 |
|---|---|---|---|
| 13 | yes | 3 | 1 × 3 = 3 |
| 6 | no | 9 | 3 (skip) |
| 3 | yes | 81 | 3 × 81 = 243 |
| 1 | yes | 6561 → 561 | 243 × 561 = 136323 → {{ANSWER}} |

3 to the 13 is {{FULL}}; its last 3 digits are {{ANSWER}}.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** start the answer at 1, not 0. Start at 0 and every multiplication stays 0, so `power(3, 13, 1000)` gives {{wrong_power(X, N, M)}} instead of {{ANSWER}}. (`1 mod m` instead of `1` keeps `m = 1` right too.)

{{CODE}}

## Complexity

| Version | Time | Space |
|---|---|---|
| Multiply n times | O(n) | O(1) |
| Fast power | O(log n) | O(1) |

## How it was tested

{{TESTED}}
