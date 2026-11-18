def reverse_list(head):
    prev = None
    curr = head
    while curr is not None:
        rest = curr.next  # save it
        curr.next = prev  # turn the arrow
        prev = curr
        curr = rest
    return prev
# ---- test harness: not on the blog ----
import sys


class ListNode:
    def __init__(self, val, nxt=None):
        self.val, self.next = val, nxt


for line in sys.stdin.read().split("\n")[:-1]:
    head = None
    for v in reversed(line.split()):
        head = ListNode(int(v), head)
    out = []
    p = reverse_list(head)
    while p:
        out.append(str(p.val))
        p = p.next
    print(" ".join(out))
