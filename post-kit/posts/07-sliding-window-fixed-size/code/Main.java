class Solution {
    // O(n) time, O(1) space
    public long maxSum(int[] nums, int k) {
        long total = 0;
        for (int i = 0; i < k; i++) {
            total = total + nums[i];
        }
        long best = total;
        for (int i = k; i < nums.length; i++) {
            total = total + nums[i] - nums[i - k];
            best = Math.max(best, total);
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
            String[] parts = line.split("\\|");
            int k = Integer.parseInt(parts[0].trim());
            int[] a = java.util.Arrays.stream(parts[1].trim().split("\\s+")).mapToInt(Integer::parseInt).toArray();
            out.append(new Solution().maxSum(a, k)).append('\n');
        }
        System.out.print(out);
    }
}
