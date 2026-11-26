// O(n) time, O(n) space
function subarraySum(nums, k) {
    const seen = new Map([[0, 1]]);   // sum -> times seen; 0 is the empty start
    let sum = 0;
    let count = 0;
    for (const x of nums) {
        sum = sum + x;
        count = count + (seen.get(sum - k) ?? 0);
        seen.set(sum, (seen.get(sum) ?? 0) + 1);
    }
    return count;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => { const [k, rest] = l.split("|"); return subarraySum(rest.trim().split(/\s+/).map(Number), Number(k)); }).join("\n"));
