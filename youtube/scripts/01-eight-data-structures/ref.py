# Every value the post 01 videos show. The structures are run here, so the numbers are real.
from collections import deque

A = [7, 2, 9, 4, 1]
S = "code"
A2, LEN, LAST = A[2], len(A), A[len(A) - 1]
SUB = S[1:]
m = {}; m["apple"] = 3
APPLE, FIG = m["apple"], "fig" in m
seen = set(); seen.add(9); seen.add(9)
SEEN_SIZE, HAS4 = len(seen), 4 in seen
st = [3]; st.append(5)
TOP = st[-1]; POPPED = st.pop(); TOP_AFTER = st[-1]
q = deque([4]); q.append(8)
FRONT = q[0]; REMOVED = q.popleft(); FRONT_AFTER = q[0]
SECOND_BOX = A[1]      # what a beginner expects a[2] to be
