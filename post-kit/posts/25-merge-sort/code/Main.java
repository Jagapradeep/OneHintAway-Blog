import java.util.Arrays;

class Solution {
    public int[] mergeSort(int[] nums) {
        if (nums.length <= 1) {
            return nums;
        }
        int middle = nums.length / 2;
        int[] left = mergeSort(Arrays.copyOfRange(nums, 0, middle));
        int[] right = mergeSort(Arrays.copyOfRange(nums, middle, nums.length));
        return merge(left, right);
    }

    private int[] merge(int[] left, int[] right) {
        int[] result = new int[left.length + right.length];
        int i = 0, j = 0, k = 0;
        while (i < left.length && j < right.length) {
            if (left[i] <= right[j]) {
                result[k++] = left[i];
                i++;
            } else {
                result[k++] = right[j];
                j++;
            }
        }
        // the rest of left and right
        while (i < left.length) result[k++] = left[i++];
        while (j < right.length) result[k++] = right[j++];
        return result;
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
            int[] a = line.isEmpty() ? new int[0] : Arrays.stream(line.split(" ")).mapToInt(Integer::parseInt).toArray();
            int[] r = new Solution().mergeSort(a);
            for (int k = 0; k < r.length; k++) out.append(k > 0 ? " " : "").append(r[k]);
            out.append('\n');
        }
        System.out.print(out);
    }
}
