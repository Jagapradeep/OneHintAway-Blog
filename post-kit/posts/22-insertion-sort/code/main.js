function insertionSort(nums) {
    for (let i = 1; i < nums.length; i++) {
        const card = nums[i];
        let j = i - 1;
        while (j >= 0 && nums[j] > card) {
            nums[j + 1] = nums[j];
            j--;
        }
        nums[j + 1] = card;
    }
    return nums;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => insertionSort(l.trim() ? l.trim().split(" ").map(Number) : []).join(" ")).join("\n"));
