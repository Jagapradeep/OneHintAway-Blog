#include <vector>
using namespace std;

vector<int> insertionSort(vector<int> nums) {
    for (int i = 1; i < (int)nums.size(); i++) {
        int card = nums[i];
        int j = i - 1;
        while (j >= 0 && nums[j] > card) {
            nums[j + 1] = nums[j];
            j--;
        }
        nums[j + 1] = card;
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
        vector<int> r = insertionSort(a);
        for (size_t k = 0; k < r.size(); k++) cout << (k ? " " : "") << r[k];
        cout << "\n";
    }
}
