import java.util.HashMap;
import java.util.Map;

class Solution {
    // O(m + n) time, O(k) space
    public String minWindow(String s, String t) {
        Map<Character, Integer> need = new HashMap<>();
        for (char c : t.toCharArray()) {
            need.put(c, need.getOrDefault(c, 0) + 1);
        }
        int missing = t.length();
        int left = 0;
        int bestStart = 0;
        int bestLen = Integer.MAX_VALUE;
        for (int right = 0; right < s.length(); right++) {
            char c = s.charAt(right);
            if (need.getOrDefault(c, 0) > 0) {
                missing = missing - 1;
            }
            need.put(c, need.getOrDefault(c, 0) - 1);
            while (missing == 0) {
                if (right - left + 1 < bestLen) {
                    bestStart = left;
                    bestLen = right - left + 1;
                }
                char d = s.charAt(left);
                need.put(d, need.get(d) + 1);
                if (need.get(d) > 0) {
                    missing = missing + 1;
                }
                left = left + 1;
            }
        }
        if (bestLen == Integer.MAX_VALUE) {
            return "";
        }
        return s.substring(bestStart, bestStart + bestLen);
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            String[] p = line.trim().split(" ");
            String r = new Solution().minWindow(p[0], p[1]);
            out.append(r.isEmpty() ? "-" : r).append('\n');
        }
        System.out.print(out);
    }
}
