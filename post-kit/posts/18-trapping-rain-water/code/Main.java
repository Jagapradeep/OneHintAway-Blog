class Solution {
    // O(n) time, O(1) space
    public long trap(int[] height) {
        int left = 0;
        int right = height.length - 1;
        int leftMax = 0;           // tallest wall seen
        int rightMax = 0;
        long water = 0;
        while (left < right) {
            if (height[left] < height[right]) {
                int bar = height[left];
                leftMax = Math.max(leftMax, bar);
                water = water + leftMax - bar;
                left = left + 1;
            } else {
                int bar = height[right];
                rightMax = Math.max(rightMax, bar);
                water = water + rightMax - bar;
                right = right - 1;
            }
        }
        return water;
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
            out.append(new Solution().trap(a)).append('\n');
        }
        System.out.print(out);
    }
}
