#include <vector>
#include <utility>
using namespace std;

class Solution {
public:
    // O(n) time, O(1) extra space
    int missingNumber(vector<int>& nums) {
        int n = nums.size();
        int i = 0;
        while (i < n) {
            int seat = nums[i];
            if (seat < n && nums[seat] != seat) {
                swap(nums[i], nums[seat]);
            } else {
                i = i + 1;          // home, or no seat
            }
        }
        for (int k = 0; k < n; k++) {
            if (nums[k] != k) {     // wrong number
                return k;
            }
        }
        return n;
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
        cout << Solution().missingNumber(a) << "\n";
    }
}
