#include <vector>
using namespace std;

// build: O(n) time, O(n) space
vector<long long> buildPrefix(const vector<int>& nums) {
    int n = nums.size();
    vector<long long> prefix(n + 1, 0);
    for (int i = 0; i < n; i++) {
        prefix[i + 1] = prefix[i] + nums[i];
    }
    return prefix;
}

// query: O(1)
long long rangeSum(const vector<long long>& prefix, int left, int right) {
    return prefix[right + 1] - prefix[left];
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
int main() {
    string line;
    while (getline(cin, line)) {
        size_t bar = line.find('|');
        istringstream in(line.substr(0, bar)); vector<int> a; int x;
        while (in >> x) a.push_back(x);
        vector<long long> p = buildPrefix(a);
        string q = line.substr(bar + 1), part; istringstream qs(q); bool first = true;
        while (getline(qs, part, ',')) {
            istringstream pq(part); int l, r; pq >> l >> r;
            cout << (first ? "" : " ") << rangeSum(p, l, r); first = false;
        }
        cout << "\n";
    }
}
