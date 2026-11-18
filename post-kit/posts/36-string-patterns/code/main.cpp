#include <string>
#include <vector>
using namespace std;

bool isPalindrome(const string& word) {
    int left = 0;
    int right = (int)word.size() - 1;
    while (left < right) {
        if (word[left] != word[right]) {
            return false;
        }
        left++;
        right--;
    }
    return true;
}

bool isAnagram(const string& s, const string& t) {
    vector<int> counts(26, 0);
    for (char letter : s) {
        int k = letter - 'a'; // alphabet index
        counts[k] = counts[k] + 1;
    }
    for (char letter : t) {
        int k = letter - 'a';
        counts[k] = counts[k] - 1;
    }
    for (int count : counts) {
        if (count != 0) {
            return false;
        }
    }
    return true;
}
// ---- test harness: not on the blog ----
#include <iostream>
int main() {
    string line;
    while (getline(cin, line)) {
        size_t bar = line.find('|');
        string s = line.substr(0, bar), t = line.substr(bar + 1);
        cout << (isAnagram(s, t) ? "true" : "false") << " " << (isPalindrome(s) ? "true" : "false") << "\n";
    }
}
