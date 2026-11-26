// build: O(n) time, O(n) space
function buildPrefix(nums) {
    const n = nums.length;
    const prefix = new Array(n + 1).fill(0);
    for (let i = 0; i < n; i++) {
        prefix[i + 1] = prefix[i] + nums[i];
    }
    return prefix;
}

// query: O(1)
function rangeSum(prefix, left, right) {
    return prefix[right + 1] - prefix[left];
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    const [a, q] = l.split("|");
    const p = buildPrefix(a.trim().split(/\s+/).map(Number));
    return q.split(",").map(s => { const [x, y] = s.trim().split(/\s+/).map(Number); return rangeSum(p, x, y); }).join(" ");
}).join("\n"));
