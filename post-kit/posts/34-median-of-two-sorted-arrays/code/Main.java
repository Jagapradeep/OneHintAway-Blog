class Solution {
    private int edge(int[] nums, int k, int empty) {
        if (k < 0 || k >= nums.length) {
            return empty;
        }
        return nums[k];
    }

    public double findMedianSortedArrays(int[] nums1, int[] nums2) {
        return median(nums1, nums2);
    }

    private double median(int[] a, int[] b) {
        if (a.length > b.length) {
            return median(b, a); // a: shorter
        }
        int m = a.length;
        int n = b.length;
        int half = (m + n + 1) / 2;
        int low = 0;
        int high = m;
        while (low < high) {
            int i = (low + high) / 2;
            if (b[half - i - 1] > a[i]) {
                low = i + 1; // more from a
            } else {
                high = i;
            }
        }
        int j = half - low; // low = the cut in a
        int leftA = edge(a, low - 1, Integer.MIN_VALUE);
        int leftB = edge(b, j - 1, Integer.MIN_VALUE);
        int leftMax = Math.max(leftA, leftB);
        if ((m + n) % 2 == 1) {
            return leftMax;
        }
        int rightA = edge(a, low, Integer.MAX_VALUE);
        int rightB = edge(b, j, Integer.MAX_VALUE);
        int rightMin = Math.min(rightA, rightB);
        return (leftMax + (double) rightMin) / 2;
    }
}
// ---- test harness: not on the blog ----
public class Main {
    static int[] parse(String s) {
        s = s.trim();
        return s.isEmpty() ? new int[0] : java.util.Arrays.stream(s.split(" ")).mapToInt(Integer::parseInt).toArray();
    }

    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            String[] parts = line.split("\\|", -1);
            double r = new Solution().findMedianSortedArrays(parse(parts[0]), parse(parts[1]));
            out.append(String.format(java.util.Locale.ROOT, "%.1f", r)).append('\n');
        }
        System.out.print(out);
    }
}
