A problem that holds a smaller copy of itself, like `factorial(4) = 4 × factorial(3)`, is a job for recursion. Worked example: **factorial(4) = {{ANSWER}}**, followed call by call.

## The walk

| Call | Waits for | Returns |
| --- | --- | --- |
| factorial(0) | nothing (base case) | 1 |
| factorial(1) | 1 × factorial(0) | 1 × 1 = 1 |
| factorial(2) | 2 × factorial(1) | 2 × 1 = 2 |
| factorial(3) | 3 × factorial(2) | 3 × 2 = 6 |
| factorial(4) | 4 × factorial(3) | 4 × 6 = 24 |

For factorial(4) the stack holds {{HEIGHT}} calls at once.

## Pseudocode

{{PSEUDOCODE}}

**The trap:** a base case the input can skip. With `if n == 1` as the base case, factorial(0) calls factorial(-1), factorial(-2) and so on until the stack runs out of room: {{wrong_factorial(0)}}.

{{CODE}}

## Complexity

| Version | Time | Space |
|---|---|---|
| Recursion | O(n) | O(n) stack |
| A loop | O(n) | O(1) |

## How it was tested

{{TESTED}}
