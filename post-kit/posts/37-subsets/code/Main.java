import java.util.ArrayList;
import java.util.List;

class Solution {
    private void build(int[] nums, int i, List<Integer> picked, List<List<Integer>> out) {
        if (i == nums.length) {
            out.add(new ArrayList<>(picked)); // a copy
        } else {
            picked.add(nums[i]); // pick
            build(nums, i + 1, picked, out);
            picked.remove(picked.size() - 1); // skip
            build(nums, i + 1, picked, out);
        }
    }

    public List<List<Integer>> subsets(int[] nums) {
        List<List<Integer>> out = new ArrayList<>();
        build(nums, 0, new ArrayList<>(), out);
        return out;
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
            List<List<Integer>> res = new Solution().subsets(a);
            for (int k = 0; k < res.size(); k++) {
                if (k > 0) out.append(',');
                List<Integer> s = res.get(k);
                for (int j = 0; j < s.size(); j++) out.append(j > 0 ? " " : "").append(s.get(j));
            }
            out.append('\n');
        }
        System.out.print(out);
    }
}
