import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    // O(n log n) time for the sort, O(n) space for the result
    public int[][] merge(int[][] intervals) {
        Arrays.sort(intervals, (a, b) -> Integer.compare(a[0], b[0]));
        List<int[]> merged = new ArrayList<>();
        merged.add(new int[]{intervals[0][0], intervals[0][1]});
        for (int i = 1; i < intervals.length; i++) {
            int start = intervals[i][0], end = intervals[i][1];
            int[] last = merged.get(merged.size() - 1);
            if (start <= last[1]) {             // overlap
                last[1] = Math.max(last[1], end);
            } else {
                merged.add(new int[]{start, end});
            }
        }
        return merged.toArray(new int[0][]);
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            String[] parts = line.split(",");
            int[][] ps = new int[parts.length][];
            for (int k = 0; k < parts.length; k++) {
                String[] ab = parts[k].trim().split("\\s+");
                ps[k] = new int[]{Integer.parseInt(ab[0]), Integer.parseInt(ab[1])};
            }
            int[][] r = new Solution().merge(ps);
            for (int k = 0; k < r.length; k++) out.append(k > 0 ? ", " : "").append(r[k][0]).append(' ').append(r[k][1]);
            out.append('\n');
        }
        System.out.print(out);
    }
}
