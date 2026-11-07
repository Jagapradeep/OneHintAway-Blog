#include <vector>
using namespace std;

int findMin(const vector<int>& nums) {
    int low = 0;
    int high = nums.size() - 1;
    while (low < high) {
        int middle = low + (high - low) / 2;
        if (nums[middle] > nums[high]) {
            low = middle + 1; // the drop is to the right
        } else {
            high = middle; // middle may be the minimum
        }
    }
    return nums[low];
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
int main() {
    string line;
    while (getline(cin, line)) {
        istringstream in(line); vector<int> a; int x;
        while (in >> x) a.push_back(x);
        cout << findMin(a) << "\n";
    }
}
