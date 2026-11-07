class Solution {
    public int minSpeed(int[] piles, int hours) {
        int low = 1;
        int high = 0;
        for (int pile : piles) high = Math.max(high, pile);
        while (low < high) {
            int speed = low + (high - low) / 2;
            if (hoursAt(piles, speed) <= hours) {
                high = speed; // fast enough
            } else {
                low = speed + 1; // too slow
            }
        }
        return low;
    }

    private long hoursAt(int[] piles, int speed) {
        long total = 0; // can pass the 32-bit limit
        for (int pile : piles) {
            total += (pile + (long) speed - 1) / speed; // ceil(pile / speed)
        }
        return total;
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
            int hours = Integer.parseInt(parts[0]);
            int[] p = java.util.Arrays.stream(parts[1].trim().split(" ")).mapToInt(Integer::parseInt).toArray();
            out.append(new Solution().minSpeed(p, hours)).append('\n');
        }
        System.out.print(out);
    }
}
