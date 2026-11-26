# O(log n) time, O(1) space
def power(x, n, m):
    answer = 1 % m
    block = x % m
    while n > 0:
        if n % 2 == 1:
            answer = (answer * block) % m
        block = (block * block) % m
        n = n // 2
    return answer
# ---- test harness: not on the blog ----
import sys
for line in sys.stdin.read().split("\n")[:-1]:
    print(power(*map(int, line.split())))
