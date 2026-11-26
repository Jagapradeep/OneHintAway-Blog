// O(n) time, O(1) space
function maxSum(nums, k) {
    let total = 0;
    for (let i = 0; i < k; i++) {
        total = total + nums[i];
    }
    let best = total;
    for (let i = k; i < nums.length; i++) {
        total = total + nums[i] - nums[i - k];
        best = Math.max(best, total);
    }
    return best;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    const [k, rest] = l.split("|");
    return maxSum(rest.trim().split(/\s+/).map(Number), Number(k));
}).join("\n"));
