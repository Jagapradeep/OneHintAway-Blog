function partition(nums, low, high) {
    const pivot = nums[high];
    let wall = low; // next slot for a small value
    for (let j = low; j <= high - 1; j++) {
        if (nums[j] < pivot) {
            [nums[wall], nums[j]] = [nums[j], nums[wall]];
            wall++;
        }
    }
    [nums[wall], nums[high]] = [nums[high], nums[wall]];
    return wall;
}

function quickSort(nums, low, high) {
    if (low < high) {
        const spot = partition(nums, low, high);
        quickSort(nums, low, spot - 1);
        quickSort(nums, spot + 1, high);
    }
}

// k-th smallest, k from 1
function quickSelect(nums, k) {
    let low = 0;
    let high = nums.length - 1;
    while (true) {
        const spot = partition(nums, low, high);
        if (spot === k - 1) {
            return nums[spot];
        }
        if (spot < k - 1) {
            low = spot + 1; // answer is right
        } else {
            high = spot - 1; // answer is left
        }
    }
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    const [k, rest] = l.split("|");
    const a = rest.trim().split(" ").map(Number);
    const b = a.slice();
    quickSort(a, 0, a.length - 1);
    return a.join(" ") + "|" + quickSelect(b, Number(k));
}).join("\n"));
