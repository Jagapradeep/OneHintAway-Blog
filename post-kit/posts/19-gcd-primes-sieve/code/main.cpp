#include <vector>
using namespace std;

int countPrimes(int n) {
    if (n < 3) {                // only 0 and 1 are below n
        return 0;
    }
    vector<bool> isPrime(n, true);
    isPrime[0] = false;
    isPrime[1] = false;
    long long p = 2;
    while (p * p < n) {
        if (isPrime[p]) {
            long long m = p * p;
            while (m < n) {
                isPrime[m] = false;
                m = m + p;
            }
        }
        p = p + 1;
    }
    int count = 0;
    for (bool b : isPrime) count += b;
    return count;
}

int gcd(int a, int b) {
    while (b != 0) {
        int remainder = a % b;
        a = b;
        b = remainder;
    }
    return a;
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
int main() {
    string line;
    while (getline(cin, line)) {
        istringstream in(line); string w; in >> w;
        if (w == "primes") { int n; in >> n; cout << countPrimes(n) << "\n"; }
        else { int a, b; in >> a >> b; cout << gcd(a, b) << "\n"; }
    }
}
