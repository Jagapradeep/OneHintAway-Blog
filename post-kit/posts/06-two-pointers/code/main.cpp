#include <vector>
using namespace std;

class Solution {
public:
    // Two pointers: O(n) time, O(1) space
    vector<int> twoSum(vector<int>& nums, int target) {
        int left = 0;
        int right = (int)nums.size() - 1;
        while (left < right) {
            long long total = (long long)nums[left] + nums[right];
            if (total == target) {
                return {left + 1, right + 1};
            } else if (total < target) {
                left = left + 1;
            } else {
                right = right - 1;
            }
        }
        return {};
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
        int t = stoi(line.substr(0, bar));
        istringstream in(line.substr(bar + 1)); vector<int> a; int x;
        while (in >> x) a.push_back(x);
        vector<int> r = Solution().twoSum(a, t);
        if (r.empty()) cout << "none\n"; else cout << r[0] << " " << r[1] << "\n";
    }
}
