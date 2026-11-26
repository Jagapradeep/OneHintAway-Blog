import java.util.HashMap;
import java.util.Map;

class Solution {
    // O(n) time, O(n) space
    public int subarraySum(int[] nums, int k) {
        Map<Long, Integer> seen = new HashMap<>();   // sum -> times seen
        seen.put(0L, 1);                             // the empty start
        long sum = 0;
        int count = 0;
        for (int x : nums) {
            sum = sum + x;
            count = count + seen.getOrDefault(sum - k, 0);
            seen.put(sum, seen.getOrDefault(sum, 0) + 1);
        }
        return count;
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
            int k = Integer.parseInt(parts[0].trim());
            int[] a = java.util.Arrays.stream(parts[1].trim().split("\\s+")).mapToInt(Integer::parseInt).toArray();
            out.append(new Solution().subarraySum(a, k)).append('\n');
        }
        System.out.print(out);
    }
}
