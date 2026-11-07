#include <vector>
#include <utility>
using namespace std;

vector<int> selectionSort(vector<int> nums) {
    int n = nums.size();
    for (int i = 0; i <= n - 2; i++) {
        int smallest = i;
        for (int j = i + 1; j <= n - 1; j++) {
            if (nums[j] < nums[smallest]) {
                smallest = j;
            }
        }
        swap(nums[i], nums[smallest]);
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
        vector<int> r = selectionSort(a);
        for (size_t k = 0; k < r.size(); k++) cout << (k ? " " : "") << r[k];
        cout << "\n";
    }
}
