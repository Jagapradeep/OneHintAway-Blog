#include <vector>
using namespace std;

// index i of the grid read row after row
int cell(const vector<vector<int>>& grid, int i) {
    int cols = grid[0].size();
    int row = i / cols;
    int col = i % cols;
    return grid[row][col];
}

bool searchMatrix(const vector<vector<int>>& grid, int target) {
    int cells = grid.size() * grid[0].size();
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
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
int main() {
    string line;
    while (getline(cin, line)) {
        size_t a = line.find('|'), b = line.find('|', a + 1);
        int target = stoi(line.substr(0, a));
        istringstream rc(line.substr(a + 1, b - a - 1)); int r, c; rc >> r >> c;
        istringstream in(line.substr(b + 1));
        vector<vector<int>> g(r, vector<int>(c));
        for (int i = 0; i < r * c; i++) in >> g[i / c][i % c];
        cout << (searchMatrix(g, target) ? "true" : "false") << "\n";
    }
}
