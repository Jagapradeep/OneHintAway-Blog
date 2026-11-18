import java.util.ArrayList;
import java.util.List;

class Solution {
    boolean safe(int[] queens, int row, int col) {
        for (int r = 0; r < row; r++) {
            int c = queens[r];
            int gap = row - r;
            if (col == c) {
                return false; // same column
            }
            if (col == c + gap || col == c - gap) {
                return false; // same diagonal
            }
        }
        return true;
    }

    private void place(int[] queens, int row, int n, List<List<String>> out) {
        if (row == n) {
            List<String> board = new ArrayList<>(); // a board drawn from queens
            for (int q : queens) {
                char[] line = new char[n];
                java.util.Arrays.fill(line, '.');
                line[q] = 'Q';
                board.add(new String(line));
            }
            out.add(board);
            return;
        }
        for (int col = 0; col < n; col++) {
            if (safe(queens, row, col)) {
                queens[row] = col; // a queen
                place(queens, row + 1, n, out);
            }
        }
    }

    public List<List<String>> solveNQueens(int n) {
        List<List<String>> out = new ArrayList<>();
        place(new int[n], 0, n, out);
        return out;
    }
}
// ---- test harness: not on the blog ----
public class Main {
    public static void main(String[] args) throws Exception {
        java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(System.in));
        StringBuilder out = new StringBuilder();
        String line;
        Solution sol = new Solution();
        while ((line = br.readLine()) != null) {
            String[] p = line.split("\\|", -1);
            if (p[0].equals("N")) {
                List<List<String>> res = sol.solveNQueens(Integer.parseInt(p[1]));
                for (int k = 0; k < res.size(); k++) {
                    if (k > 0) out.append('|');
                    out.append(String.join(",", res.get(k)));
                }
            } else {
                String qs = p[1].trim();
                int[] q = qs.isEmpty() ? new int[0] : java.util.Arrays.stream(qs.split(" ")).mapToInt(Integer::parseInt).toArray();
                int row = Integer.parseInt(p[2]);
                int[] full = java.util.Arrays.copyOf(q, row + 1);
                out.append(sol.safe(full, row, Integer.parseInt(p[3])));
            }
            out.append('\n');
        }
        System.out.print(out);
    }
}
