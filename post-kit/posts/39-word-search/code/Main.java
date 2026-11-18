class Solution {
    private static final int[][] MOVES = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}}; // down, up, right, left

    private boolean walk(char[][] grid, String word, int row, int col, int i) {
        if (grid[row][col] != word.charAt(i)) {
            return false;
        }
        if (i == word.length() - 1) {
            return true;
        }
        grid[row][col] = '#'; // in use
        for (int[] m : MOVES) { // each cell next to [row, col]
            int r = row + m[0], c = col + m[1];
            if (r >= 0 && r < grid.length && c >= 0 && c < grid[0].length) {
                if (walk(grid, word, r, c, i + 1)) {
                    return true;
                }
            }
        }
        grid[row][col] = word.charAt(i); // undo
        return false;
    }

    public boolean exist(char[][] grid, String word) {
        for (int row = 0; row < grid.length; row++) {
            for (int col = 0; col < grid[0].length; col++) {
                if (walk(grid, word, row, col, 0)) {
                    return true;
                }
            }
        }
        return false;
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            String[] p = line.split("\\|");
            String[] rows = p[1].split("/");
            char[][] g = new char[rows.length][];
            for (int i = 0; i < rows.length; i++) g[i] = rows[i].toCharArray();
            out.append(new Solution().exist(g, p[0])).append('\n');
        }
        System.out.print(out);
    }
}
