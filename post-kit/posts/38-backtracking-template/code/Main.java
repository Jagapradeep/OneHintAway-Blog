import java.util.ArrayList;
import java.util.List;

class Solution {
    private List<List<Integer>> permute(int[] nums, boolean[] used, List<Integer> path, List<List<Integer>> out) {
        if (path.size() == nums.length) {
            out.add(new ArrayList<>(path));
            return out;
        }
        for (int i = 0; i < nums.length; i++) {
            if (!used[i]) {
                used[i] = true; // choose
                path.add(nums[i]);
                permute(nums, used, path, out);
                path.remove(path.size() - 1); // undo
                used[i] = false;
            }
        }
        return out;
    }

    private List<List<Integer>> find(int[] nums, int i, int left, List<Integer> path, List<List<Integer>> out) {
        if (left == 0) {
            out.add(new ArrayList<>(path));
            return out;
        }
        for (int j = i; j < nums.length; j++) {
            if (nums[j] <= left) {
                path.add(nums[j]); // choose
                int rest = left - nums[j];
                find(nums, j, rest, path, out);
                path.remove(path.size() - 1); // undo
            }
        }
        return out;
    }

    public List<List<Integer>> permute(int[] nums) {
        return permute(nums, new boolean[nums.length], new ArrayList<>(), new ArrayList<>());
    }

    public List<List<Integer>> combinationSum(int[] candidates, int target) {
        return find(candidates, 0, target, new ArrayList<>(), new ArrayList<>());
    }
}
// ---- test harness: not on the blog ----
public class Main {
    static int[] parse(String s) {
        return java.util.Arrays.stream(s.trim().split(" ")).mapToInt(Integer::parseInt).toArray();
    }

    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            String[] p = line.split("\\|");
            List<List<Integer>> res = p[0].equals("P") ? new Solution().permute(parse(p[1]))
                    : new Solution().combinationSum(parse(p[2]), Integer.parseInt(p[1]));
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
