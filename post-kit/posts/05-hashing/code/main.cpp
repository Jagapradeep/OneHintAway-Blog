#include <vector>
#include <unordered_map>
using namespace std;

class Solution {
public:
    // Hash map: O(n) time, O(n) space
    vector<int> twoSum(vector<int>& nums, int target) {
        unordered_map<int, int> seen;   // value -> index
        for (int i = 0; i < (int)nums.size(); i++) {
            int need = target - nums[i];
            if (seen.count(need)) {
                return {seen[need], i};
            }
            seen[nums[i]] = i;
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
