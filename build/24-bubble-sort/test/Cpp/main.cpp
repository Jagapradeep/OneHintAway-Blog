#include <vector>
#include <utility>
using namespace std;

vector<int> bubbleSort(vector<int> nums) {
    int n = nums.size();
    for (int sweep = 1; sweep <= n - 1; sweep++) {
        bool swapped = false;
        for (int j = 0; j <= n - 1 - sweep; j++) {
            if (nums[j] > nums[j + 1]) {
                swap(nums[j], nums[j + 1]);
                swapped = true;
            }
        }
        if (!swapped) {
            return nums; // already sorted
        }
    }
    return nums;
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
        vector<int> r = bubbleSort(a);
        for (size_t k = 0; k < r.size(); k++) cout << (k ? " " : "") << r[k];
        cout << "\n";
    }
}
