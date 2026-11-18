import java.util.ArrayList;
import java.util.List;

class Solution {
    public void rotate(int[][] grid) {
        int n = grid.length;
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                int t = grid[i][j];
                grid[i][j] = grid[j][i];
                grid[j][i] = t;
            }
        }
        for (int[] row : grid) {
            for (int a = 0, b = n - 1; a < b; a++, b--) {
                int t = row[a];
                row[a] = row[b];
                row[b] = t;
            }
        }
    }

    public List<Integer> spiralOrder(int[][] grid) {
        int top = 0;
        int bottom = grid.length - 1;
        int left = 0;
        int right = grid[0].length - 1;
        List<Integer> result = new ArrayList<>();
        while (top <= bottom && left <= right) {
            for (int col = left; col <= right; col++) {
                result.add(grid[top][col]);
            }
            top++;
            for (int row = top; row <= bottom; row++) {
                result.add(grid[row][right]);
            }
            right--;
            if (top > bottom || left > right) {
                return result; // nothing left
            }
            for (int col = right; col >= left; col--) {
                result.add(grid[bottom][col]);
            }
            bottom--;
            for (int row = bottom; row >= top; row--) {
                result.add(grid[row][left]);
            }
            left++;
        }
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
            String[] parts = line.split("\\|");
            String[] mn = parts[0].trim().split(" ");
            int m = Integer.parseInt(mn[0]), n = Integer.parseInt(mn[1]);
            String[] v = parts[1].trim().split(" ");
            int[][] g = new int[m][n];
            for (int i = 0; i < m * n; i++) g[i / n][i % n] = Integer.parseInt(v[i]);
            StringBuilder sb = new StringBuilder();
            for (int x : new Solution().spiralOrder(g)) sb.append(sb.length() > 0 ? " " : "").append(x);
            sb.append('|');
            if (m == n) {
                new Solution().rotate(g);
                for (int i = 0; i < m * n; i++) sb.append(i > 0 ? " " : "").append(g[i / n][i % n]);
            } else sb.append('-');
            out.append(sb).append('\n');
        }
        System.out.print(out);
    }
}
