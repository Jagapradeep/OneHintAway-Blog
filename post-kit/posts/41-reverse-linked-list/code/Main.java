class Solution {
    public ListNode reverseList(ListNode head) {
        ListNode prev = null;
        ListNode curr = head;
        while (curr != null) {
            ListNode rest = curr.next; // save it
            curr.next = prev; // turn the arrow
            prev = curr;
            curr = rest;
        }
        return prev;
    }
}
// ---- test harness: not on the blog ----
class ListNode {
    int val;
    ListNode next;
    ListNode(int val, ListNode next) { this.val = val; this.next = next; }
}

public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            String[] v = line.isEmpty() ? new String[0] : line.split(" ");
            ListNode head = null;
            for (int i = v.length - 1; i >= 0; i--) head = new ListNode(Integer.parseInt(v[i]), head);
            StringBuilder sb = new StringBuilder();
            for (ListNode p = new Solution().reverseList(head); p != null; p = p.next) sb.append(sb.length() > 0 ? " " : "").append(p.val);
            out.append(sb).append('\n');
        }
        System.out.print(out);
    }
}
