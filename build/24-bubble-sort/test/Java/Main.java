class Solution {
    public int[] bubbleSort(int[] nums) {
        int n = nums.length;
        for (int sweep = 1; sweep <= n - 1; sweep++) {
            boolean swapped = false;
            for (int j = 0; j <= n - 1 - sweep; j++) {
                if (nums[j] > nums[j + 1]) {
                    int temp = nums[j];
                    nums[j] = nums[j + 1];
                    nums[j + 1] = temp;
                    swapped = true;
                }
            }
            if (!swapped) {
                return nums; // already sorted
            }
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
            int[] r = new Solution().bubbleSort(a);
            for (int k = 0; k < r.length; k++) out.append(k > 0 ? " " : "").append(r[k]);
            out.append('\n');
        }
        System.out.print(out);
    }
}
