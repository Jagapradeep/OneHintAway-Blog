def middle_node(head):
    slow = head
    fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
    return slow


def has_cycle(head):
    slow = head
    fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next  # 1 step
        fast = fast.next.next  # 2 steps
        if slow is fast:
            return True  # fast caught up: a loop
    return False
# ---- test harness: not on the blog ----
import sys


class ListNode:
    def __init__(self, val):
        self.val, self.next = val, None


for line in sys.stdin.read().split("\n")[:-1]:
    v, p = line.split("|")
    nodes = [ListNode(int(x)) for x in v.split()]
    for a, b in zip(nodes, nodes[1:]):
        a.next = b
    if int(p) >= 0:
        nodes[-1].next = nodes[int(p)]
    head = nodes[0] if nodes else None
    if has_cycle(head):
        print("true")
    else:
        m = middle_node(head)
        print("false " + (str(m.val) if m else "none"))
