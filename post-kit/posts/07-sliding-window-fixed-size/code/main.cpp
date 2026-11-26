#include <vector>
#include <algorithm>
using namespace std;

class Solution {
public:
    // O(n) time, O(1) space
    long long maxSum(vector<int>& nums, int k) {
        long long total = 0;
        for (int i = 0; i < k; i++) {
            total = total + nums[i];
        }
        long long best = total;
        for (int i = k; i < (int)nums.size(); i++) {
            total = total + nums[i] - nums[i - k];
            best = max(best, total);
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
        int k = stoi(line.substr(0, bar));
        istringstream in(line.substr(bar + 1)); vector<int> a; int x;
        while (in >> x) a.push_back(x);
        cout << Solution().maxSum(a, k) << "\n";
    }
}
