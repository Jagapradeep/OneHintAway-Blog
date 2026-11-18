#include <vector>
#include <cmath>
using namespace std;

long long pumpsNeeded(const vector<int>& stations, double d) {
    long long count = 0;
    for (int i = 1; i < (int)stations.size(); i++) {
        double gap = stations[i] - stations[i - 1];
        count += (long long)ceil(gap / d) - 1;
    }
    return count;
}

double minMaxGap(const vector<int>& stations, int k) {
    int n = stations.size();
    double low = 0;
    double high = stations[n - 1] - stations[0];
    while (high - low > 0.000001) {
        double d = (low + high) / 2;
        if (pumpsNeeded(stations, d) <= k) {
            high = d; // fits: go lower
        } else {
            low = d; // too many: go higher
        }
    }
    return high;
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
        int k = stoi(line.substr(0, bar));
        istringstream in(line.substr(bar + 1)); vector<int> st; int x;
        while (in >> x) st.push_back(x);
        printf("%.2f\n", minMaxGap(st, k));
    }
}
