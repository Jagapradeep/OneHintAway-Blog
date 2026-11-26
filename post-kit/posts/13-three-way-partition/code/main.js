// O(n) time, O(1) space: one pass, in place
function sortColors(nums) {
    let low = 0;                  // next 0 goes here
    let mid = 0;                  // number to check
    let high = nums.length - 1;   // next 2 goes here
    while (mid <= high) {
        if (nums[mid] === 0) {
            [nums[low], nums[mid]] = [nums[mid], nums[low]];
            low = low + 1;
            mid = mid + 1;
        } else if (nums[mid] === 1) {
            mid = mid + 1;
        } else {
            [nums[mid], nums[high]] = [nums[high], nums[mid]];
            high = high - 1;      // mid stays
        }
    }
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => { const a = l.trim().split(/\s+/).map(Number); sortColors(a); return a.join(" "); }).join("\n"));
