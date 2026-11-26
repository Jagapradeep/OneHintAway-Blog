class Solution:
    # O(m + n) time, O(k) space
    def minWindow(self, s: str, t: str) -> str:
        need = {}
        for c in t:
            need[c] = need.get(c, 0) + 1
        missing = len(t)
        left = 0
        best_start = 0
        best_len = float("inf")
        for right in range(len(s)):
            c = s[right]
            if need.get(c, 0) > 0:
                missing = missing - 1
            need[c] = need.get(c, 0) - 1
            while missing == 0:
                if right - left + 1 < best_len:
                    best_start = left
                    best_len = right - left + 1
                d = s[left]
                need[d] = need[d] + 1
                if need[d] > 0:
                    missing = missing + 1
                left = left + 1
        if best_len == float("inf"):
            return ""
        return s[best_start:best_start + best_len]
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    s, t = line.split()
    print(Solution().minWindow(s, t) or "-")
