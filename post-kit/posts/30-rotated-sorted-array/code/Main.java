class Solution {
    public int findMin(int[] nums) {
        int low = 0;
        int high = nums.length - 1;
        while (low < high) {
            int middle = low + (high - low) / 2;
            if (nums[middle] > nums[high]) {
                low = middle + 1; // the drop is to the right
            } else {
                high = middle; // middle may be the minimum
            }
        }
        return nums[low];
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            int[] a = java.util.Arrays.stream(line.trim().split(" ")).mapToInt(Integer::parseInt).toArray();
            out.append(new Solution().findMin(a)).append('\n');
        }
        System.out.print(out);
    }
}
