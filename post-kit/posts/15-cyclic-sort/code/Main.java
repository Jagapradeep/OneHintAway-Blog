class Solution {
    // O(n) time, O(1) extra space
    public int missingNumber(int[] nums) {
        int n = nums.length;
        int i = 0;
        while (i < n) {
            int seat = nums[i];
            if (seat < n && nums[seat] != seat) {
                nums[i] = nums[seat];
                nums[seat] = seat;
            } else {
                i = i + 1;          // home, or no seat
            }
        }
        for (int k = 0; k < n; k++) {
            if (nums[k] != k) {     // wrong number
                return k;
            }
        }
        return n;
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
            out.append(new Solution().missingNumber(a)).append('\n');
        }
        System.out.print(out);
    }
}
