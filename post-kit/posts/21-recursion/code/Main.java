class Solution {
    // O(n) time, O(n) stack space. long holds factorial(n) up to n = 20.
    public long factorial(int n) {
        if (n == 0) {
            return 1;            // base case
        }
        return n * factorial(n - 1);
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            out.append(new Solution().factorial(Integer.parseInt(line.trim()))).append('\n');
        }
        System.out.print(out);
    }
}
