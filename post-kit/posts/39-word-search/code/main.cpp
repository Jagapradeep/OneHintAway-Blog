#include <vector>
#include <string>
using namespace std;

const int MOVES[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}}; // down, up, right, left

bool walk(vector<string>& grid, const string& word, int row, int col, int i) {
    if (grid[row][col] != word[i]) {
        return false;
    }
    if (i == (int)word.size() - 1) {
        return true;
    }
    grid[row][col] = '#'; // in use
    for (auto& m : MOVES) { // each cell next to [row, col]
        int r = row + m[0], c = col + m[1];
        if (r >= 0 && r < (int)grid.size() && c >= 0 && c < (int)grid[0].size()) {
            if (walk(grid, word, r, c, i + 1)) {
                return true;
            }
        }
    }
    grid[row][col] = word[i]; // undo
    return false;
}

bool exist(vector<string>& grid, const string& word) {
    for (int row = 0; row < (int)grid.size(); row++) {
        for (int col = 0; col < (int)grid[0].size(); col++) {
            if (walk(grid, word, row, col, 0)) {
                return true;
            }
        }
    }
    return false;
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
int main() {
    string line;
    while (getline(cin, line)) {
        size_t bar = line.find('|');
        string w = line.substr(0, bar), rest = line.substr(bar + 1);
        vector<string> g; stringstream ss(rest); string r;
        while (getline(ss, r, '/')) g.push_back(r);
        cout << (exist(g, w) ? "true" : "false") << "\n";
    }
}
