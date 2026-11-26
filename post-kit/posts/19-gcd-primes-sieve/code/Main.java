class Solution {
    public int countPrimes(int n) {
        if (n < 3) {                // only 0 and 1 are below n
            return 0;
        }
        boolean[] isPrime = new boolean[n];
        java.util.Arrays.fill(isPrime, true);
        isPrime[0] = false;
        isPrime[1] = false;
        long p = 2;
        while (p * p < n) {
            if (isPrime[(int) p]) {
                long m = p * p;
                while (m < n) {
                    isPrime[(int) m] = false;
                    m = m + p;
                }
            }
            p = p + 1;
        }
        int count = 0;
        for (boolean b : isPrime) if (b) count++;
        return count;
    }

    public int gcd(int a, int b) {
        while (b != 0) {
            int remainder = a % b;
            a = b;
            b = remainder;
        }
        return a;
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        Solution s = new Solution();
        while ((line = br.readLine()) != null) {
            String[] w = line.trim().split("\\s+");
            out.append(w[0].equals("primes") ? s.countPrimes(Integer.parseInt(w[1])) : s.gcd(Integer.parseInt(w[1]), Integer.parseInt(w[2]))).append('\n');
        }
        System.out.print(out);
    }
}
