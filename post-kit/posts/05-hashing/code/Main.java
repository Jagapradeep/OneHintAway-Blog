import java.util.HashMap;
import java.util.Map;

class Solution {
    // Hash map: O(n) time, O(n) space
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> seen = new HashMap<>();   // value -> index
        for (int i = 0; i < nums.length; i++) {
            int need = target - nums[i];
            if (seen.containsKey(need)) {
                return new int[]{seen.get(need), i};
            }
            seen.put(nums[i], i);
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
