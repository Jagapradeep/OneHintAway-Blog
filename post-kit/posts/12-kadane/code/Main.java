class Solution {
    // O(n) time, O(1) space
    public int maxSubArray(int[] nums) {
        int current = 0;        // sum so far
        int best = nums[0];     // largest so far
        for (int x : nums) {
            if (current < 0) {  // in debt?
                current = 0;    // start fresh
            }
            current = current + x;
            best = Math.max(best, current);
        }
        return best;
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            int[] a = java.util.Arrays.stream(line.trim().split("\\s+")).mapToInt(Integer::parseInt).toArray();
            out.append(new Solution().maxSubArray(a)).append('\n');
        }
        System.out.print(out);
    }
}
