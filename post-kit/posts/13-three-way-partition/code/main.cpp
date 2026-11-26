#include <vector>
#include <utility>
using namespace std;

class Solution {
public:
    // O(n) time, O(1) space: one pass, in place
    void sortColors(vector<int>& nums) {
        int low = 0;                      // next 0 goes here
        int mid = 0;                      // number to check
        int high = (int)nums.size() - 1;  // next 2 goes here
        while (mid <= high) {
            if (nums[mid] == 0) {
                swap(nums[low], nums[mid]);
                low = low + 1;
                mid = mid + 1;
            } else if (nums[mid] == 1) {
                mid = mid + 1;
            } else {
                swap(nums[mid], nums[high]);
                high = high - 1;          // mid stays
            }
        }
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
        Solution().sortColors(a);
        for (size_t k = 0; k < a.size(); k++) cout << (k ? " " : "") << a[k];
        cout << "\n";
    }
}
