class Solution {
    public void quickSort(int[] nums, int low, int high) {
        if (low < high) {
            int spot = partition(nums, low, high);
            quickSort(nums, low, spot - 1);
            quickSort(nums, spot + 1, high);
        }
    }

    // k-th smallest, k from 1
    public int quickSelect(int[] nums, int k) {
        int low = 0;
        int high = nums.length - 1;
        while (true) {
            int spot = partition(nums, low, high);
            if (spot == k - 1) {
                return nums[spot];
            }
            if (spot < k - 1) {
                low = spot + 1; // answer is right
            } else {
                high = spot - 1; // answer is left
            }
        }
    }

    private int partition(int[] nums, int low, int high) {
        int pivot = nums[high];
        int wall = low; // next slot for a small value
        for (int j = low; j <= high - 1; j++) {
            if (nums[j] < pivot) {
                swap(nums, wall, j);
                wall++;
            }
        }
        swap(nums, wall, high);
        return wall;
    }

    private void swap(int[] nums, int a, int b) {
        int temp = nums[a];
        nums[a] = nums[b];
        nums[b] = temp;
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
            int k = Integer.parseInt(parts[0]);
            int[] a = java.util.Arrays.stream(parts[1].trim().split(" ")).mapToInt(Integer::parseInt).toArray();
            int[] b = a.clone();
            Solution s = new Solution();
            s.quickSort(a, 0, a.length - 1);
            int kth = s.quickSelect(b, k);
            for (int i = 0; i < a.length; i++) out.append(i > 0 ? " " : "").append(a[i]);
            out.append('|').append(kth).append('\n');
        }
        System.out.print(out);
    }
}
