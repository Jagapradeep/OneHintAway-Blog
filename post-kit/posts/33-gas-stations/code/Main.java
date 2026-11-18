class Solution {
    private long pumpsNeeded(int[] stations, double d) {
        long count = 0;
        for (int i = 1; i < stations.length; i++) {
            double gap = stations[i] - stations[i - 1];
            count += (long) Math.ceil(gap / d) - 1;
        }
        return count;
    }

    public double minMaxGap(int[] stations, int k) {
        int n = stations.length;
        double low = 0;
        double high = stations[n - 1] - stations[0];
        while (high - low > 0.000001) {
            double d = (low + high) / 2;
            if (pumpsNeeded(stations, d) <= k) {
                high = d; // fits: go lower
            } else {
                low = d; // too many: go higher
            }
        }
        return high;
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
            int[] st = java.util.Arrays.stream(parts[1].trim().split(" ")).mapToInt(Integer::parseInt).toArray();
            out.append(String.format(java.util.Locale.ROOT, "%.2f", new Solution().minMaxGap(st, k))).append('\n');
        }
        System.out.print(out);
    }
}
