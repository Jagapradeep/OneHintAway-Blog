#include <vector>
#include <string>
using namespace std;

bool safe(const vector<int>& queens, int row, int col) {
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

void place(vector<int>& queens, int row, int n, vector<vector<string>>& out) {
    if (row == n) {
        vector<string> board; // a board drawn from queens
        for (int q : queens) {
            string line(n, '.');
            line[q] = 'Q';
            board.push_back(line);
        }
        out.push_back(board);
        return;
    }
    for (int col = 0; col < n; col++) {
        if (safe(queens, row, col)) {
            queens[row] = col; // a queen
            place(queens, row + 1, n, out);
        }
    }
}

vector<vector<string>> solveNQueens(int n) {
    vector<vector<string>> out;
    vector<int> queens(n, 0);
    place(queens, 0, n, out);
    return out;
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
int main() {
    string line;
    while (getline(cin, line)) {
        vector<string> p; size_t a = 0, b;
        while ((b = line.find('|', a)) != string::npos) { p.push_back(line.substr(a, b - a)); a = b + 1; }
        p.push_back(line.substr(a));
        if (p[0] == "N") {
            vector<vector<string>> res = solveNQueens(stoi(p[1]));
            for (size_t k = 0; k < res.size(); k++) {
                if (k) cout << "|";
                for (size_t j = 0; j < res[k].size(); j++) cout << (j ? "," : "") << res[k][j];
            }
        } else {
            istringstream in(p[1]); vector<int> q; int x;
            while (in >> x) q.push_back(x);
            cout << (safe(q, stoi(p[2]), stoi(p[3])) ? "true" : "false");
        }
        cout << "\n";
    }
}
