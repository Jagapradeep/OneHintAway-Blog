#include <vector>
using namespace std;

class Solution {
public:
    // O(n) time, O(1) space. LeetCode 169 promises a majority.
    int majorityElement(vector<int>& nums) {
        int candidate = 0;
        int count = 0;
        for (int x : nums) {
            if (count == 0) {
                candidate = x;   // new candidate
            }
            if (x == candidate) {
                count = count + 1;
            } else {
                count = count - 1;
            }
        }
        return candidate;
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
        cout << Solution().majorityElement(a) << "\n";
    }
}
