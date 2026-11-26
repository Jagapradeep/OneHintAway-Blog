class Solution {
    // Two pointers: O(n) time, O(1) space
    public int[] twoSum(int[] nums, int target) {
        int left = 0;
        int right = nums.length - 1;
        while (left < right) {
            long total = (long) nums[left] + nums[right];
            if (total == target) {
                return new int[]{left + 1, right + 1};
            } else if (total < target) {
                left = left + 1;
            } else {
                right = right - 1;
            }
        }
        return null;
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
            int t = Integer.parseInt(parts[0].trim());
            int[] a = java.util.Arrays.stream(parts[1].trim().split("\\s+")).mapToInt(Integer::parseInt).toArray();
            int[] r = new Solution().twoSum(a, t);
            out.append(r == null ? "none" : r[0] + " " + r[1]).append('\n');
        }
        System.out.print(out);
    }
}
