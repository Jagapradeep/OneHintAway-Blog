#include <vector>
using namespace std;

void build(const vector<int>& nums, int i, vector<int>& picked, vector<vector<int>>& out) {
    if (i == (int)nums.size()) {
        out.push_back(picked); // a copy
    } else {
        picked.push_back(nums[i]); // pick
        build(nums, i + 1, picked, out);
        picked.pop_back(); // skip
        build(nums, i + 1, picked, out);
    }
}

vector<vector<int>> subsets(const vector<int>& nums) {
    vector<vector<int>> out;
    vector<int> picked;
    build(nums, 0, picked, out);
    return out;
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
int main() {
    string line;
    while (getline(cin, line)) {
        istringstream in(line); vector<int> a; int x;
        while (in >> x) a.push_back(x);
        vector<vector<int>> res = subsets(a);
        for (size_t k = 0; k < res.size(); k++) {
            if (k) cout << ",";
            for (size_t j = 0; j < res[k].size(); j++) cout << (j ? " " : "") << res[k][j];
        }
        cout << "\n";
    }
}
