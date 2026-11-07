#include <vector>
using namespace std;

// first index whose value is >= target
int lowerBound(const vector<int>& nums, int target) {
    int low = 0;
    int high = nums.size(); // one past the end
    while (low < high) {
        int middle = low + (high - low) / 2;
        if (nums[middle] < target) {
            low = middle + 1;
        } else {
            high = middle; // could be the answer
        }
    }
    return low;
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
int main() {
    string line;
    while (getline(cin, line)) {
        size_t bar = line.find('|');
        int target = stoi(line.substr(0, bar));
        istringstream in(line.substr(bar + 1)); vector<int> a; int x;
        while (in >> x) a.push_back(x);
        cout << lowerBound(a, target) << " " << lowerBound(a, target + 1) << "\n";
    }
}
