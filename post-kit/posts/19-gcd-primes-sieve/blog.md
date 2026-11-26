Clues: **count the primes below n**, or **find the GCD of two numbers**. Worked example: **LeetCode 204, Count Primes** (Medium).

## The walk

Below 12: cross out 4, 6, 8, 10 for 2, then 9 for 3, then stop because 4 × 4 ≥ 12. Left: {{sp(PRIMES)}}, so **{{COUNT}}**.

`gcd(18, 12)`: 18 mod 12 = 6, then 12 mod 6 = 0, so the GCD is {{gcd(18, 12)}}.

## Pseudocode

{{PSEUDOCODE}}

```
function gcd(a, b):
    while b != 0:
        remainder = a mod b
        a = b
        b = remainder
    return a
```

**The trap:** mark 0 and 1. They start as true; forget the line that sets them to false and `countPrimes(10)` returns {{wrong_count_primes(10)}} instead of {{count_primes(10)}}.

{{CODE}}

## Complexity

| | Time | Space |
|---|---|---|
| Sieve | O(n log log n) | O(n) |
| GCD | O(log min(a, b)) | O(1) |

## How it was tested

{{TESTED}}
