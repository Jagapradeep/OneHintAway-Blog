#include <vector>
#include <algorithm>
using namespace std;

class Solution {
public:
    // O(n) time, O(1) space. Every number must be positive.
    int longestWithin(vector<int>& nums, long long budget) {
        int left = 0;
        long long total = 0;
        int best = 0;
        for (int right = 0; right < (int)nums.size(); right++) {
            total = total + nums[right];
            while (total > budget) {
                total = total - nums[left];
                left = left + 1;
            }
            best = max(best, right - left + 1);
        }
        return best;
    }
};
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
int main() {
    string line;
    while (getline(cin, line)) {
        size_t bar = line.find('|');
        long long b = stoll(line.substr(0, bar));
        istringstream in(line.substr(bar + 1)); vector<int> a; int x;
        while (in >> x) a.push_back(x);
        cout << Solution().longestWithin(a, b) << "\n";
    }
}
