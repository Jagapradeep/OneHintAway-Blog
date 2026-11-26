// Two pointers: O(n) time, O(1) space
function twoSum(nums, target) {
    let left = 0;
    let right = nums.length - 1;
    while (left < right) {
        const total = nums[left] + nums[right];
        if (total === target) {
            return [left + 1, right + 1];
        } else if (total < target) {
            left = left + 1;
        } else {
            right = right - 1;
        }
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
