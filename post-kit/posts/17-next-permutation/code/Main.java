class Solution {
    // O(n) time, O(1) extra space
    public void nextPermutation(int[] nums) {
        int n = nums.length;
        int i = n - 2;
        while (i >= 0 && nums[i] >= nums[i + 1]) {
            i = i - 1;                // walk left
        }
        if (i >= 0) {                 // pivot found
            int j = n - 1;
            while (nums[j] <= nums[i]) {
                j = j - 1;
            }
            int t = nums[i]; nums[i] = nums[j]; nums[j] = t;
        }
        for (int lo = i + 1, hi = n - 1; lo < hi; lo++, hi--) {
            int t = nums[lo]; nums[lo] = nums[hi]; nums[hi] = t;
        }
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
            new Solution().nextPermutation(a);
            for (int k = 0; k < a.length; k++) out.append(k > 0 ? " " : "").append(a[k]);
            out.append('\n');
        }
        System.out.print(out);
    }
}
