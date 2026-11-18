class Solution {
    public ListNode middleNode(ListNode head) {
        ListNode slow = head;
        ListNode fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
        }
        return slow;
    }

    public boolean hasCycle(ListNode head) {
        ListNode slow = head;
        ListNode fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next; // 1 step
            fast = fast.next.next; // 2 steps
            if (slow == fast) {
                return true; // fast caught up: a loop
            }
        }
        return false;
    }
}
// ---- test harness: not on the blog ----
class ListNode {
    int val;
    ListNode next;
    ListNode(int val) { this.val = val; }
}

public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        Solution sol = new Solution();
        while ((line = br.readLine()) != null) {
            String[] p = line.split("\\|");
            String vs = p[0].trim();
            String[] v = vs.isEmpty() ? new String[0] : vs.split(" ");
            int pos = Integer.parseInt(p[1]);
            ListNode[] nodes = new ListNode[v.length];
            for (int i = 0; i < v.length; i++) nodes[i] = new ListNode(Integer.parseInt(v[i]));
            for (int i = 0; i + 1 < v.length; i++) nodes[i].next = nodes[i + 1];
            if (pos >= 0) nodes[v.length - 1].next = nodes[pos];
            ListNode head = v.length > 0 ? nodes[0] : null;
            if (sol.hasCycle(head)) out.append("true");
            else {
                ListNode m = sol.middleNode(head);
                out.append("false ").append(m == null ? "none" : String.valueOf(m.val));
            }
            out.append('\n');
        }
        System.out.print(out);
    }
}
