// O(n) time, O(1) space
function maxSubArray(nums) {
    let current = 0;        // sum so far
    let best = nums[0];     // largest so far
    for (const x of nums) {
        if (current < 0) {  // in debt?
            current = 0;    // start fresh
        }
        current = current + x;
        best = Math.max(best, current);
    }
    return best;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => maxSubArray(l.trim().split(/\s+/).map(Number))).join("\n"));
