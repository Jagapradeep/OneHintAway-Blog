#include <vector>
#include <algorithm>
using namespace std;

class Solution {
public:
    // O(n) time, O(1) space
    int maxSubArray(vector<int>& nums) {
        int current = 0;        // sum so far
        int best = nums[0];     // largest so far
        for (int x : nums) {
            if (current < 0) {  // in debt?
                current = 0;    // start fresh
            }
            current = current + x;
            best = max(best, current);
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
        istringstream in(line); vector<int> a; int x;
        while (in >> x) a.push_back(x);
        cout << Solution().maxSubArray(a) << "\n";
    }
}
