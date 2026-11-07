class Solution {
    // first index whose value is >= target
    public int lowerBound(int[] nums, int target) {
        int low = 0;
        int high = nums.length; // one past the end
        while (low < high) {
            int middle = low + (high - low) / 2;
            if (nums[middle] < target) {
                low = middle + 1;
            } else {
                high = middle; // could be the answer
            }
        }
        return low;
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            int bar = line.indexOf('|');
            int target = Integer.parseInt(line.substring(0, bar));
            String rest = line.substring(bar + 1).trim();
            int[] a = rest.isEmpty() ? new int[0] : java.util.Arrays.stream(rest.split(" ")).mapToInt(Integer::parseInt).toArray();
            Solution s = new Solution();
            out.append(s.lowerBound(a, target)).append(' ').append(s.lowerBound(a, target + 1)).append('\n');
        }
        System.out.print(out);
    }
}
