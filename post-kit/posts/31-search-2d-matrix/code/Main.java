class Solution {
    public boolean searchMatrix(int[][] grid, int target) {
        int cells = grid.length * grid[0].length;
        int low = 0;
        int high = cells - 1;
        while (low <= high) {
            int middle = low + (high - low) / 2;
            if (cell(grid, middle) == target) {
                return true;
            } else if (cell(grid, middle) < target) {
                low = middle + 1;
            } else {
                high = middle - 1;
            }
        }
        return false;
    }

    // index i of the grid read row after row
    private int cell(int[][] grid, int i) {
        int cols = grid[0].length;
        int row = i / cols;
        int col = i % cols;
        return grid[row][col];
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
            int target = Integer.parseInt(parts[0]);
            String[] rc = parts[1].trim().split(" ");
            int r = Integer.parseInt(rc[0]), c = Integer.parseInt(rc[1]);
            String[] v = parts[2].trim().split(" ");
            int[][] g = new int[r][c];
            for (int i = 0; i < r * c; i++) g[i / c][i % c] = Integer.parseInt(v[i]);
            out.append(new Solution().searchMatrix(g, target)).append('\n');
        }
        System.out.print(out);
    }
}
