function bubbleSort(nums) {
    const n = nums.length;
    for (let sweep = 1; sweep <= n - 1; sweep++) {
        let swapped = false;
        for (let j = 0; j <= n - 1 - sweep; j++) {
            if (nums[j] > nums[j + 1]) {
                [nums[j], nums[j + 1]] = [nums[j + 1], nums[j]];
                swapped = true;
            }
        }
        if (!swapped) {
            return nums; // already sorted
        }
    }
    return nums;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => bubbleSort(l.trim() ? l.trim().split(" ").map(Number) : []).join(" ")).join("\n"));
