// O(n) time, O(1) extra space
function missingNumber(nums) {
    const n = nums.length;
    let i = 0;
    while (i < n) {
        const seat = nums[i];
        if (seat < n && nums[seat] !== seat) {
            [nums[i], nums[seat]] = [nums[seat], nums[i]];
        } else {
            i = i + 1;          // home, or no seat
        }
    }
    for (let k = 0; k < n; k++) {
        if (nums[k] !== k) {    // wrong number
            return k;
        }
    }
    return n;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => missingNumber(l.trim().split(/\s+/).map(Number))).join("\n"));
