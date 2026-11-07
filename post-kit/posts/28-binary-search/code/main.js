function search(nums, target) {
    let low = 0;
    let high = nums.length - 1;
    while (low <= high) {
        const middle = low + Math.floor((high - low) / 2);
        if (nums[middle] === target) {
            return middle;
        } else if (nums[middle] < target) {
            low = middle + 1;
        } else {
            high = middle - 1;
        }
    }
    return -1;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    const [t, rest] = l.split("|");
    return search(rest.trim().split(" ").map(Number), Number(t));
}).join("\n"));
