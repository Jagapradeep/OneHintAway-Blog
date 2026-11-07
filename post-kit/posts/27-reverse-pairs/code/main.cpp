#include <vector>
using namespace std;

void merge(vector<int>& nums, int low, int mid, int high) {
    vector<int> merged;
    int a = low, b = mid + 1;
    while (a <= mid && b <= high) {
        merged.push_back(nums[a] <= nums[b] ? nums[a++] : nums[b++]);
    }
    while (a <= mid) merged.push_back(nums[a++]);
    while (b <= high) merged.push_back(nums[b++]);
    for (int k = 0; k < (int)merged.size(); k++) nums[low + k] = merged[k];
}

int countPairs(vector<int>& nums, int low, int high) {
    if (low >= high) {
        return 0;
    }
    int mid = (low + high) / 2;
    int left = countPairs(nums, low, mid);
    int right = countPairs(nums, mid + 1, high);
    int count = left + right;
    int i = low;
    for (int j = mid + 1; j <= high; j++) {
        long long twice = 2LL * nums[j]; // 64-bit: no overflow
        while (i <= mid && nums[i] <= twice) {
            i++;
        }
        count += mid - i + 1;
    }
    merge(nums, low, mid, high); // the merge from post 25
    return count;
}

int reversePairs(vector<int>& nums) {
    int n = nums.size();
    return countPairs(nums, 0, n - 1);
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
        cout << reversePairs(a) << "\n";
    }
}
