function mergeSort(nums) {
    if (nums.length <= 1) {
        return nums;
    }
    const middle = Math.floor(nums.length / 2);
    const left = mergeSort(nums.slice(0, middle));
    const right = mergeSort(nums.slice(middle));
    return merge(left, right);
}

function merge(left, right) {
    const result = [];
    let i = 0;
    let j = 0;
    while (i < left.length && j < right.length) {
        if (left[i] <= right[j]) {
            result.push(left[i]);
            i++;
        } else {
            result.push(right[j]);
            j++;
        }
    }
    return result.concat(left.slice(i), right.slice(j));
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => mergeSort(l.trim() ? l.trim().split(" ").map(Number) : []).join(" ")).join("\n"));
