class Solution {
    public boolean isPalindrome(String word) {
        int left = 0;
        int right = word.length() - 1;
        while (left < right) {
            if (word.charAt(left) != word.charAt(right)) {
                return false;
            }
            left++;
            right--;
        }
        return true;
    }

    public boolean isAnagram(String s, String t) {
        int[] counts = new int[26];
        for (char letter : s.toCharArray()) {
            int k = letter - 'a'; // alphabet index
            counts[k] = counts[k] + 1;
        }
        for (char letter : t.toCharArray()) {
            int k = letter - 'a';
            counts[k] = counts[k] - 1;
        }
        for (int count : counts) {
            if (count != 0) {
                return false;
            }
        }
        return true;
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        Solution sol = new Solution();
        while ((line = br.readLine()) != null) {
            String[] p = line.split("\\|");
            out.append(sol.isAnagram(p[0], p[1])).append(' ').append(sol.isPalindrome(p[0])).append('\n');
        }
        System.out.print(out);
    }
}
