#include <vector>
#include <algorithm>
using namespace std;

class Solution {
public:
    // O(n) time, O(1) space
    long long trap(vector<int>& height) {
        int left = 0;
        int right = (int)height.size() - 1;
        int leftMax = 0;           // tallest wall seen
        int rightMax = 0;
        long long water = 0;
        while (left < right) {
            if (height[left] < height[right]) {
                int bar = height[left];
                leftMax = max(leftMax, bar);
                water = water + leftMax - bar;
                left = left + 1;
            } else {
                int bar = height[right];
                rightMax = max(rightMax, bar);
                water = water + rightMax - bar;
                right = right - 1;
            }
        }
        return water;
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
        cout << Solution().trap(a) << "\n";
    }
}
