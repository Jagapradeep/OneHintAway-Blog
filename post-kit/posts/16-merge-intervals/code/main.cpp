#include <vector>
#include <algorithm>
using namespace std;

class Solution {
public:
    // O(n log n) time for the sort, O(n) space for the result
    vector<vector<int>> merge(vector<vector<int>>& intervals) {
        sort(intervals.begin(), intervals.end(), [](const vector<int>& a, const vector<int>& b) { return a[0] < b[0]; });
        vector<vector<int>> merged;
        merged.push_back({intervals[0][0], intervals[0][1]});
        for (int i = 1; i < (int)intervals.size(); i++) {
            int start = intervals[i][0], end = intervals[i][1];
            vector<int>& last = merged.back();
            if (start <= last[1]) {             // overlap
                last[1] = max(last[1], end);
            } else {
                merged.push_back({start, end});
            }
        }
        return merged;
    }
};
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
int main() {
    string line;
    while (getline(cin, line)) {
        vector<vector<int>> ps; string part; istringstream all(line);
        while (getline(all, part, ',')) { istringstream in(part); int a, b; in >> a >> b; ps.push_back({a, b}); }
        vector<vector<int>> r = Solution().merge(ps);
        for (size_t k = 0; k < r.size(); k++) cout << (k ? ", " : "") << r[k][0] << " " << r[k][1];
        cout << "\n";
    }
}
