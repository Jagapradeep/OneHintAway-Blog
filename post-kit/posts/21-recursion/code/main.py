class Solution:
    # O(n) time, O(n) stack space
    def factorial(self, n: int) -> int:
        if n == 0:
            return 1             # base case
        return n * self.factorial(n - 1)
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    print(Solution().factorial(int(line)))
