#include <vector>
using namespace std;

vector<vector<int>>& permute(const vector<int>& nums, vector<bool>& used, vector<int>& path, vector<vector<int>>& out) {
    if (path.size() == nums.size()) {
        out.push_back(path);
        return out;
    }
    for (int i = 0; i < (int)nums.size(); i++) {
        if (!used[i]) {
            used[i] = true; // choose
            path.push_back(nums[i]);
            permute(nums, used, path, out);
            path.pop_back(); // undo
            used[i] = false;
        }
    }
    return out;
}

vector<vector<int>>& find(const vector<int>& nums, int i, int left, vector<int>& path, vector<vector<int>>& out) {
    if (left == 0) {
        out.push_back(path);
        return out;
    }
    for (int j = i; j < (int)nums.size(); j++) {
        if (nums[j] <= left) {
            path.push_back(nums[j]); // choose
            int rest = left - nums[j];
            find(nums, j, rest, path, out);
            path.pop_back(); // undo
        }
    }
    return out;
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
static vector<int> parse(const string& s) { istringstream in(s); vector<int> v; int x; while (in >> x) v.push_back(x); return v; }
int main() {
    string line;
    while (getline(cin, line)) {
        vector<string> p; size_t a = 0, b;
        while ((b = line.find('|', a)) != string::npos) { p.push_back(line.substr(a, b - a)); a = b + 1; }
        p.push_back(line.substr(a));
        vector<vector<int>> out; vector<int> path;
        if (p[0] == "P") {
            vector<int> nums = parse(p[1]); vector<bool> used(nums.size(), false);
            permute(nums, used, path, out);
        } else {
            find(parse(p[2]), 0, stoi(p[1]), path, out);
        }
        for (size_t k = 0; k < out.size(); k++) {
            if (k) cout << ",";
            for (size_t j = 0; j < out[k].size(); j++) cout << (j ? " " : "") << out[k][j];
        }
        cout << "\n";
    }
}
