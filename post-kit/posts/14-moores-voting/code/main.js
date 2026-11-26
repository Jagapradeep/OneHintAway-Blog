// O(n) time, O(1) space. LeetCode 169 promises a majority.
function majorityElement(nums) {
    let candidate = null;
    let count = 0;
    for (const x of nums) {
        if (count === 0) {
            candidate = x;   // new candidate
        }
        if (x === candidate) {
            count = count + 1;
        } else {
            count = count - 1;
        }
    }
    return candidate;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => majorityElement(l.trim().split(/\s+/).map(Number))).join("\n"));
