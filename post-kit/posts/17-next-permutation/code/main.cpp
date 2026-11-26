#include <vector>
#include <algorithm>
using namespace std;

class Solution {
public:
    // O(n) time, O(1) extra space
    void nextPermutation(vector<int>& nums) {
        int n = nums.size();
        int i = n - 2;
        while (i >= 0 && nums[i] >= nums[i + 1]) {
            i = i - 1;                // walk left
        }
        if (i >= 0) {                 // pivot found
            int j = n - 1;
            while (nums[j] <= nums[i]) {
                j = j - 1;
            }
            swap(nums[i], nums[j]);
        }
        reverse(nums.begin() + i + 1, nums.end());
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
        Solution().nextPermutation(a);
        for (size_t k = 0; k < a.size(); k++) cout << (k ? " " : "") << a[k];
        cout << "\n";
    }
}
