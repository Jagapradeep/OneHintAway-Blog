function reversePairs(nums) {
    const n = nums.length;
    return countPairs(nums, 0, n - 1);
}

function countPairs(nums, low, high) {
    if (low >= high) {
        return 0;
    }
    const mid = Math.floor((low + high) / 2);
    const left = countPairs(nums, low, mid);
    const right = countPairs(nums, mid + 1, high);
    let count = left + right;
    let i = low;
    for (let j = mid + 1; j <= high; j++) {
        const twice = 2 * nums[j];
        while (i <= mid && nums[i] <= twice) {
            i++;
        }
        count += mid - i + 1;
    }
    merge(nums, low, mid, high); // the merge from post 25
    return count;
}

function merge(nums, low, mid, high) {
    const merged = [];
    let a = low, b = mid + 1;
    while (a <= mid && b <= high) {
        merged.push(nums[a] <= nums[b] ? nums[a++] : nums[b++]);
    }
    while (a <= mid) merged.push(nums[a++]);
    while (b <= high) merged.push(nums[b++]);
    for (let k = 0; k < merged.length; k++) nums[low + k] = merged[k];
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => reversePairs(l.trim().split(" ").map(Number))).join("\n"));
