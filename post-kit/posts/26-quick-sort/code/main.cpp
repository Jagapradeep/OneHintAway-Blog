#include <vector>
#include <utility>
using namespace std;

int partition(vector<int>& nums, int low, int high) {
    int pivot = nums[high];
    int wall = low; // next slot for a small value
    for (int j = low; j <= high - 1; j++) {
        if (nums[j] < pivot) {
            swap(nums[wall], nums[j]);
            wall++;
        }
    }
    swap(nums[wall], nums[high]);
    return wall;
}

void quickSort(vector<int>& nums, int low, int high) {
    if (low < high) {
        int spot = partition(nums, low, high);
        quickSort(nums, low, spot - 1);
        quickSort(nums, spot + 1, high);
    }
}

// k-th smallest, k from 1
int quickSelect(vector<int>& nums, int k) {
    int low = 0;
    int high = nums.size() - 1;
    while (true) {
        int spot = partition(nums, low, high);
        if (spot == k - 1) {
            return nums[spot];
        }
        if (spot < k - 1) {
            low = spot + 1; // answer is right
        } else {
            high = spot - 1; // answer is left
        }
    }
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
int main() {
    string line;
    while (getline(cin, line)) {
        size_t bar = line.find('|');
        int k = stoi(line.substr(0, bar));
        istringstream in(line.substr(bar + 1)); vector<int> a; int x;
        while (in >> x) a.push_back(x);
        vector<int> b = a;
        quickSort(a, 0, (int)a.size() - 1);
        int kth = quickSelect(b, k);
        for (size_t i = 0; i < a.size(); i++) cout << (i ? " " : "") << a[i];
        cout << "|" << kth << "\n";
    }
}
