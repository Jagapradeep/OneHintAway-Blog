// O(n) time, O(n) stack space. long long holds factorial(n) up to n = 20.
class Solution {
public:
    long long factorial(int n) {
        if (n == 0) {
            return 1;            // base case
        }
        return n * factorial(n - 1);
    }
};
// ---- test harness: not on the blog ----
#include <iostream>
using namespace std;
int main() {
    int n;
    while (cin >> n) cout << Solution().factorial(n) << "\n";
}
