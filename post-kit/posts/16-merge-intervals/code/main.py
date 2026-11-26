class Solution:
    # O(n log n) time for the sort, O(n) space for the result
    def merge(self, intervals: list[list[int]]) -> list[list[int]]:
        intervals.sort(key=lambda pair: pair[0])
        merged = []
        merged.append([intervals[0][0], intervals[0][1]])
        for i in range(1, len(intervals)):
            start, end = intervals[i]
            last = merged[-1]
            if start <= last[1]:                # overlap
                last[1] = max(last[1], end)
            else:
                merged.append([start, end])
        return merged
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    ps = [[int(x) for x in p.split()] for p in line.split(",")]
    print(", ".join(f"{a} {b}" for a, b in Solution().merge(ps)))
