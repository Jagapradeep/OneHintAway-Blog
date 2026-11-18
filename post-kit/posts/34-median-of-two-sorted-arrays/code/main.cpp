#include <vector>
#include <climits>
#include <algorithm>
using namespace std;

int edge(const vector<int>& nums, int k, int empty) {
    if (k < 0 || k >= (int)nums.size()) {
        return empty;
    }
    return nums[k];
}

double median(const vector<int>& a, const vector<int>& b) {
    if (a.size() > b.size()) {
        return median(b, a); // a: shorter
    }
    int m = a.size();
    int n = b.size();
    int half = (m + n + 1) / 2;
    int low = 0;
    int high = m;
    while (low < high) {
        int i = (low + high) / 2;
        if (b[half - i - 1] > a[i]) {
            low = i + 1; // more from a
        } else {
            high = i;
        }
    }
    int j = half - low; // low = the cut in a
    int leftA = edge(a, low - 1, INT_MIN);
    int leftB = edge(b, j - 1, INT_MIN);
    int leftMax = max(leftA, leftB);
    if ((m + n) % 2 == 1) {
        return leftMax;
    }
    int rightA = edge(a, low, INT_MAX);
    int rightB = edge(b, j, INT_MAX);
    int rightMin = min(rightA, rightB);
    return (leftMax + (double)rightMin) / 2;
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
#include <cstdio>
int main() {
    string line;
    while (getline(cin, line)) {
        size_t bar = line.find('|');
        vector<int> a, b; int x;
        istringstream ia(line.substr(0, bar)); while (ia >> x) a.push_back(x);
        istringstream ib(line.substr(bar + 1)); while (ib >> x) b.push_back(x);
        printf("%.1f\n", median(a, b));
    }
}
