function reverseList(head) {
    let prev = null;
    let curr = head;
    while (curr !== null) {
        const rest = curr.next; // save it
        curr.next = prev; // turn the arrow
        prev = curr;
        curr = rest;
    }
    return prev;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    let head = null;
    const v = l.trim() ? l.trim().split(" ").map(Number) : [];
    for (let i = v.length - 1; i >= 0; i--) head = { val: v[i], next: head };
    const out = [];
    for (let p = reverseList(head); p !== null; p = p.next) out.push(p.val);
    return out.join(" ");
}).join("\n"));
