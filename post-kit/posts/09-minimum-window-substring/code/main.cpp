#include <string>
#include <unordered_map>
#include <climits>
using namespace std;

class Solution {
public:
    // O(m + n) time, O(k) space
    string minWindow(string s, string t) {
        unordered_map<char, int> need;
        for (char c : t) {
            need[c] = need[c] + 1;
        }
        int missing = t.size();
        int left = 0;
        int bestStart = 0;
        int bestLen = INT_MAX;
        for (int right = 0; right < (int)s.size(); right++) {
            char c = s[right];
            if (need[c] > 0) {
                missing = missing - 1;
            }
            need[c] = need[c] - 1;
            while (missing == 0) {
                if (right - left + 1 < bestLen) {
                    bestStart = left;
                    bestLen = right - left + 1;
                }
                char d = s[left];
                need[d] = need[d] + 1;
                if (need[d] > 0) {
                    missing = missing + 1;
                }
                left = left + 1;
            }
        }
        if (bestLen == INT_MAX) {
            return "";
        }
        return s.substr(bestStart, bestLen);
    }
};
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
int main() {
    string line;
    while (getline(cin, line)) {
        istringstream in(line); string s, t; in >> s >> t;
        string r = Solution().minWindow(s, t);
        cout << (r.empty() ? "-" : r) << "\n";
    }
}
