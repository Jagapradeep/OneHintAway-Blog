// O(log n) time, O(1) space. m is at most about 2^31, so block * block fits in 64 bits.
long long power(long long x, long long n, long long m) {
    long long answer = 1 % m;
    long long block = x % m;
    while (n > 0) {
        if (n % 2 == 1) {
            answer = (answer * block) % m;
        }
        block = (block * block) % m;
        n = n / 2;
    }
    return answer;
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <string>
using namespace std;
int main() {
    long long x, n, m;
    while (cin >> x >> n >> m) cout << power(x, n, m) << "\n";
}
