// O(n) time, O(1) space. Every number must be positive.
function longestWithin(nums, budget) {
    let left = 0;
    let total = 0;
    let best = 0;
    for (let right = 0; right < nums.length; right++) {
        total = total + nums[right];
        while (total > budget) {
            total = total - nums[left];
            left = left + 1;
        }
        best = Math.max(best, right - left + 1);
    }
    return best;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    const [b, rest] = l.split("|");
    return longestWithin(rest.trim().split(/\s+/).map(Number), Number(b));
}).join("\n"));
