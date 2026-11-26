// O(n) time, O(1) extra space
function nextPermutation(nums) {
    const n = nums.length;
    let i = n - 2;
    while (i >= 0 && nums[i] >= nums[i + 1]) {
        i = i - 1;                // walk left
    }
    if (i >= 0) {                 // pivot found
        let j = n - 1;
        while (nums[j] <= nums[i]) {
            j = j - 1;
        }
        [nums[i], nums[j]] = [nums[j], nums[i]];
    }
    for (let lo = i + 1, hi = n - 1; lo < hi; lo++, hi--) {
        [nums[lo], nums[hi]] = [nums[hi], nums[lo]];
    }
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => { const a = l.trim().split(/\s+/).map(Number); nextPermutation(a); return a.join(" "); }).join("\n"));
