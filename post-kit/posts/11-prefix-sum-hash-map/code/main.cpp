#include <vector>
#include <unordered_map>
using namespace std;

class Solution {
public:
    // O(n) time, O(n) space
    int subarraySum(vector<int>& nums, int k) {
        unordered_map<long long, int> seen;   // sum -> times seen
        seen[0] = 1;                          // the empty start
        long long sum = 0;
        int count = 0;
        for (int x : nums) {
            sum = sum + x;
            auto it = seen.find(sum - k);
            count = count + (it == seen.end() ? 0 : it->second);
            seen[sum] = seen[sum] + 1;
        }
        return count;
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
        cout << Solution().subarraySum(a, k) << "\n";
    }
}
