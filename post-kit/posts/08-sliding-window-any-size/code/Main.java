class Solution {
    // O(n) time, O(1) space. Every number must be positive.
    public int longestWithin(int[] nums, long budget) {
        int left = 0;
        long total = 0;
        int best = 0;
        for (int right = 0; right < nums.length; right++) {
            total = total + nums[right];
            while (total > budget) {
                total = total - nums[left];
                left = left + 1;
            }
            best = Math.max(best, right - left + 1);
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
            long b = Long.parseLong(parts[0].trim());
            int[] a = java.util.Arrays.stream(parts[1].trim().split("\\s+")).mapToInt(Integer::parseInt).toArray();
            out.append(new Solution().longestWithin(a, b)).append('\n');
        }
        System.out.print(out);
    }
}
