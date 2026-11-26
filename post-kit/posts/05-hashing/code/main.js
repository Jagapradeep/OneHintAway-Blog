// Hash map: O(n) time, O(n) space
function twoSum(nums, target) {
    const seen = new Map();   // value -> index
    for (let i = 0; i < nums.length; i++) {
        const need = target - nums[i];
        if (seen.has(need)) {
            return [seen.get(need), i];
        }
        seen.set(nums[i], i);
    }
    return null;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    const [t, rest] = l.split("|");
    const r = twoSum(rest.trim().split(/\s+/).map(Number), Number(t));
    return r === null ? "none" : r.join(" ");
}).join("\n"));
