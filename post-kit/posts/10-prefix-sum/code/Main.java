class Solution {
    // build: O(n) time, O(n) space
    public long[] buildPrefix(int[] nums) {
        int n = nums.length;
        long[] prefix = new long[n + 1];
        for (int i = 0; i < n; i++) {
            prefix[i + 1] = prefix[i] + nums[i];
        }
        return prefix;
    }

    // query: O(1)
    public long rangeSum(long[] prefix, int left, int right) {
        return prefix[right + 1] - prefix[left];
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        Solution sol = new Solution();
        while ((line = br.readLine()) != null) {
            String[] parts = line.split("\\|");
            int[] a = java.util.Arrays.stream(parts[0].trim().split("\\s+")).mapToInt(Integer::parseInt).toArray();
            long[] p = sol.buildPrefix(a);
            String[] qs = parts[1].split(",");
            for (int k = 0; k < qs.length; k++) {
                String[] lr = qs[k].trim().split("\\s+");
                out.append(k > 0 ? " " : "").append(sol.rangeSum(p, Integer.parseInt(lr[0]), Integer.parseInt(lr[1])));
            }
            out.append('\n');
        }
        System.out.print(out);
    }
}
