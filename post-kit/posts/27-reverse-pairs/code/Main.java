class Solution {
    public int reversePairs(int[] nums) {
        int n = nums.length;
        return countPairs(nums, 0, n - 1);
    }

    private int countPairs(int[] nums, int low, int high) {
        if (low >= high) {
            return 0;
        }
        int mid = (low + high) / 2;
        int left = countPairs(nums, low, mid);
        int right = countPairs(nums, mid + 1, high);
        int count = left + right;
        int i = low;
        for (int j = mid + 1; j <= high; j++) {
            long twice = 2L * nums[j]; // 64-bit: no overflow
            while (i <= mid && nums[i] <= twice) {
                i++;
            }
            count += mid - i + 1;
        }
        merge(nums, low, mid, high); // the merge from post 25
        return count;
    }

    private void merge(int[] nums, int low, int mid, int high) {
        int[] merged = new int[high - low + 1];
        int a = low, b = mid + 1, k = 0;
        while (a <= mid && b <= high) {
            merged[k++] = nums[a] <= nums[b] ? nums[a++] : nums[b++];
        }
        while (a <= mid) merged[k++] = nums[a++];
        while (b <= high) merged[k++] = nums[b++];
        System.arraycopy(merged, 0, nums, low, merged.length);
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            int[] a = java.util.Arrays.stream(line.trim().split(" ")).mapToInt(Integer::parseInt).toArray();
            out.append(new Solution().reversePairs(a)).append('\n');
        }
        System.out.print(out);
    }
}
