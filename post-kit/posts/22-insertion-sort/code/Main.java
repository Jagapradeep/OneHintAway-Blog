class Solution {
    public int[] insertionSort(int[] nums) {
        for (int i = 1; i < nums.length; i++) {
            int card = nums[i];
            int j = i - 1;
            while (j >= 0 && nums[j] > card) {
                nums[j + 1] = nums[j];
                j--;
            }
            nums[j + 1] = card;
        }
        return nums;
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            int[] a = line.isEmpty() ? new int[0] : java.util.Arrays.stream(line.split(" ")).mapToInt(Integer::parseInt).toArray();
            int[] r = new Solution().insertionSort(a);
            for (int k = 0; k < r.length; k++) out.append(k > 0 ? " " : "").append(r[k]);
            out.append('\n');
        }
        System.out.print(out);
    }
}
