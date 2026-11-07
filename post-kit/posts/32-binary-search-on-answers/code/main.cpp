#include <vector>
#include <algorithm>
using namespace std;

long long hoursAt(const vector<int>& piles, int speed) {
    long long total = 0; // can pass the 32-bit limit
    for (int pile : piles) {
        total += (pile + (long long)speed - 1) / speed; // ceil(pile / speed)
    }
    return total;
}

int minSpeed(const vector<int>& piles, int hours) {
    int low = 1;
    int high = *max_element(piles.begin(), piles.end());
    while (low < high) {
        int speed = low + (high - low) / 2;
        if (hoursAt(piles, speed) <= hours) {
            high = speed; // fast enough
        } else {
            low = speed + 1; // too slow
        }
    }
    return low;
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
int main() {
    string line;
    while (getline(cin, line)) {
        size_t bar = line.find('|');
        int hours = stoi(line.substr(0, bar));
        istringstream in(line.substr(bar + 1)); vector<int> p; int x;
        while (in >> x) p.push_back(x);
        cout << minSpeed(p, hours) << "\n";
    }
}
