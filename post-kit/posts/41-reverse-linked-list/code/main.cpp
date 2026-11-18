// LeetCode defines ListNode like this:
struct ListNode {
    int val;
    ListNode* next;
    ListNode(int v, ListNode* n) : val(v), next(n) {}
};

ListNode* reverseList(ListNode* head) {
    ListNode* prev = nullptr;
    ListNode* curr = head;
    while (curr != nullptr) {
        ListNode* rest = curr->next; // save it
        curr->next = prev; // turn the arrow
        prev = curr;
        curr = rest;
    }
    return prev;
}
// ---- test harness: not on the blog ----
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;
int main() {
    string line;
    while (getline(cin, line)) {
        istringstream in(line); vector<int> v; int x;
        while (in >> x) v.push_back(x);
        ListNode* head = nullptr;
        for (int i = (int)v.size() - 1; i >= 0; i--) head = new ListNode(v[i], head);
        bool first = true;
        for (ListNode* p = reverseList(head); p; p = p->next) { cout << (first ? "" : " ") << p->val; first = false; }
        cout << "\n";
    }
}
