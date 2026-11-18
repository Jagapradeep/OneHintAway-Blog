function middleNode(head) {
    let slow = head;
    let fast = head;
    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
    }
    return slow;
}

function hasCycle(head) {
    let slow = head;
    let fast = head;
    while (fast !== null && fast.next !== null) {
        slow = slow.next; // 1 step
        fast = fast.next.next; // 2 steps
        if (slow === fast) {
            return true; // fast caught up: a loop
        }
    }
    return false;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    const [v, p] = l.split("|");
    const nodes = (v.trim() ? v.trim().split(" ") : []).map(x => ({ val: Number(x), next: null }));
    for (let i = 0; i + 1 < nodes.length; i++) nodes[i].next = nodes[i + 1];
    if (Number(p) >= 0) nodes[nodes.length - 1].next = nodes[Number(p)];
    const head = nodes.length ? nodes[0] : null;
    if (hasCycle(head)) return "true";
    const m = middleNode(head);
    return "false " + (m ? m.val : "none");
}).join("\n"));
