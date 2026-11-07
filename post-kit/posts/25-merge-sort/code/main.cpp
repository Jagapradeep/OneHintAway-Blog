#include <vector>
using namespace std;

vector<int> merge(const vector<int>& left, const vector<int>& right) {
    vector<int> result;
    size_t i = 0, j = 0;
    while (i < left.size() && j < right.size()) {
        if (left[i] <= right[j]) {
            result.push_back(left[i]);
            i++;
        } else {
            result.push_back(right[j]);
            j++;
        }
    }
    // the rest of left and right
    result.insert(result.end(), left.begin() + i, left.end());
    result.insert(result.end(), right.begin() + j, right.end());
    return result;
}

vector<int> mergeSort(const vector<int>& nums) {
    if (nums.size() <= 1) {
        return nums;
    }
    size_t middle = nums.size() / 2;
    vector<int> left = mergeSort(vector<int>(nums.begin(), nums.begin() + middle));
    vector<int> right = mergeSort(vector<int>(nums.begin() + middle, nums.end()));
    return merge(left, right);
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
        vector<int> r = mergeSort(a);
        for (size_t k = 0; k < r.size(); k++) cout << (k ? " " : "") << r[k];
        cout << "\n";
    }
}
