// first index whose value is >= target
function lowerBound(nums, target) {
    let low = 0;
    let high = nums.length; // one past the end
    while (low < high) {
        const middle = Math.floor((low + high) / 2);
        if (nums[middle] < target) {
            low = middle + 1;
        } else {
            high = middle; // could be the answer
        }
    }
    return low;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    const [t, rest] = l.split("|");
    const a = rest.trim() ? rest.trim().split(" ").map(Number) : [];
    return lowerBound(a, Number(t)) + " " + lowerBound(a, Number(t) + 1);
}).join("\n"));
