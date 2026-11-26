class Solution {
    // O(n) time, O(1) space: one pass, in place
    public void sortColors(int[] nums) {
        int low = 0;                  // next 0 goes here
        int mid = 0;                  // number to check
        int high = nums.length - 1;   // next 2 goes here
        while (mid <= high) {
            if (nums[mid] == 0) {
                int t = nums[low]; nums[low] = nums[mid]; nums[mid] = t;
                low = low + 1;
                mid = mid + 1;
            } else if (nums[mid] == 1) {
                mid = mid + 1;
            } else {
                int t = nums[mid]; nums[mid] = nums[high]; nums[high] = t;
                high = high - 1;      // mid stays
            }
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
            new Solution().sortColors(a);
            for (int k = 0; k < a.length; k++) out.append(k > 0 ? " " : "").append(a[k]);
            out.append('\n');
        }
        System.out.print(out);
    }
}
