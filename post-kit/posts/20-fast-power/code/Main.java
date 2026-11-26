class Solution {
    // O(log n) time, O(1) space. m is at most about 2^31, so block * block fits in a long.
    public long power(long x, long n, long m) {
        long answer = 1 % m;
        long block = x % m;
        while (n > 0) {
            if (n % 2 == 1) {
                answer = (answer * block) % m;
            }
            block = (block * block) % m;
            n = n / 2;
        }
        return answer;
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            String[] w = line.trim().split("\\s+");
            out.append(new Solution().power(Long.parseLong(w[0]), Long.parseLong(w[1]), Long.parseLong(w[2]))).append('\n');
        }
        System.out.print(out);
    }
}
