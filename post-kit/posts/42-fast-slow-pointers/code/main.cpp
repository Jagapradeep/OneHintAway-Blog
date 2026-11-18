// LeetCode defines ListNode like this:
struct ListNode {
    int val;
    ListNode* next;
    ListNode(int v) : val(v), next(nullptr) {}
};

ListNode* middleNode(ListNode* head) {
    ListNode* slow = head;
    ListNode* fast = head;
    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next;
        fast = fast->next->next;
    }
    return slow;
}

bool hasCycle(ListNode* head) {
    ListNode* slow = head;
    ListNode* fast = head;
    while (fast != nullptr && fast->next != nullptr) {
        slow = slow->next; // 1 step
        fast = fast->next->next; // 2 steps
        if (slow == fast) {
            return true; // fast caught up: a loop
        }
    }
    return false;
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
        size_t bar = line.find('|');
        istringstream in(line.substr(0, bar)); vector<ListNode*> nodes; int x;
        while (in >> x) nodes.push_back(new ListNode(x));
        int pos = stoi(line.substr(bar + 1));
        for (size_t i = 0; i + 1 < nodes.size(); i++) nodes[i]->next = nodes[i + 1];
        if (pos >= 0) nodes.back()->next = nodes[pos];
        ListNode* head = nodes.empty() ? nullptr : nodes[0];
        if (hasCycle(head)) cout << "true\n";
        else {
            ListNode* m = middleNode(head);
            cout << "false " << (m ? to_string(m->val) : string("none")) << "\n";
        }
    }
}
