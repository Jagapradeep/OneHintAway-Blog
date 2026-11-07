#include <vector>
using namespace std;

int search(const vector<int>& nums, int target) {
    int low = 0;
    int high = nums.size() - 1;
    while (low <= high) {
        int middle = low + (high - low) / 2;
        if (nums[middle] == target) {
            return middle;
        } else if (nums[middle] < target) {
            low = middle + 1;
        } else {
            high = middle - 1;
        }
    }
    return -1;
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
        cout << search(a, target) << "\n";
    }
}
