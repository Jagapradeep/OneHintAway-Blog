function selectionSort(nums) {
    const n = nums.length;
    for (let i = 0; i <= n - 2; i++) {
        let smallest = i;
        for (let j = i + 1; j <= n - 1; j++) {
            if (nums[j] < nums[smallest]) {
                smallest = j;
            }
        }
        [nums[i], nums[smallest]] = [nums[smallest], nums[i]];
    }
    return nums;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => selectionSort(l.trim() ? l.trim().split(" ").map(Number) : []).join(" ")).join("\n"));
