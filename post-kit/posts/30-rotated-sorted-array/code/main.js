function findMin(nums) {
    let low = 0;
    let high = nums.length - 1;
    while (low < high) {
        const middle = Math.floor((low + high) / 2);
        if (nums[middle] > nums[high]) {
            low = middle + 1; // the drop is to the right
        } else {
            high = middle; // middle may be the minimum
        }
    }
    return nums[low];
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => findMin(l.trim().split(" ").map(Number))).join("\n"));
