class Solution {
    public int[] selectionSort(int[] nums) {
        int n = nums.length;
        for (int i = 0; i <= n - 2; i++) {
            int smallest = i;
            for (int j = i + 1; j <= n - 1; j++) {
                if (nums[j] < nums[smallest]) {
                    smallest = j;
                }
            }
            int temp = nums[i];
            nums[i] = nums[smallest];
            nums[smallest] = temp;
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
            int[] r = new Solution().selectionSort(a);
            for (int k = 0; k < r.length; k++) out.append(k > 0 ? " " : "").append(r[k]);
            out.append('\n');
        }
        System.out.print(out);
    }
}
