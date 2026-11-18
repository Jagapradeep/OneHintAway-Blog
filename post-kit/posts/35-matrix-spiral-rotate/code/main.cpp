#include <vector>
#include <algorithm>
using namespace std;

void rotate(vector<vector<int>>& grid) {
    int n = grid.size();
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            swap(grid[i][j], grid[j][i]);
        }
    }
    for (auto& row : grid) {
        reverse(row.begin(), row.end());
    }
}

vector<int> spiralOrder(const vector<vector<int>>& grid) {
    int top = 0;
    int bottom = grid.size() - 1;
    int left = 0;
    int right = grid[0].size() - 1;
    vector<int> result;
    while (top <= bottom && left <= right) {
        for (int col = left; col <= right; col++) {
            result.push_back(grid[top][col]);
        }
        top++;
        for (int row = top; row <= bottom; row++) {
            result.push_back(grid[row][right]);
        }
        right--;
        if (top > bottom || left > right) {
            return result; // nothing left
        }
        for (int col = right; col >= left; col--) {
            result.push_back(grid[bottom][col]);
        }
        bottom--;
        for (int row = bottom; row >= top; row--) {
            result.push_back(grid[row][left]);
        }
        left++;
    }
    return result;
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
int main() {
    string line;
    while (getline(cin, line)) {
        size_t bar = line.find('|');
        istringstream h(line.substr(0, bar)); int m, n; h >> m >> n;
        istringstream in(line.substr(bar + 1));
        vector<vector<int>> g(m, vector<int>(n));
        for (int i = 0; i < m * n; i++) in >> g[i / n][i % n];
        vector<int> s = spiralOrder(g);
        for (size_t k = 0; k < s.size(); k++) cout << (k ? " " : "") << s[k];
        cout << "|";
        if (m == n) {
            rotate(g);
            for (int i = 0; i < m * n; i++) cout << (i ? " " : "") << g[i / n][i % n];
        } else cout << "-";
        cout << "\n";
    }
}
