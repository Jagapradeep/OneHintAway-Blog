class Solution {
    // O(n) time, O(1) space. LeetCode 169 promises a majority.
    public int majorityElement(int[] nums) {
        int candidate = 0;
        int count = 0;
        for (int x : nums) {
            if (count == 0) {
                candidate = x;   // new candidate
            }
            if (x == candidate) {
                count = count + 1;
            } else {
                count = count - 1;
            }
        }
        return candidate;
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
            out.append(new Solution().majorityElement(a)).append('\n');
        }
        System.out.print(out);
    }
}
