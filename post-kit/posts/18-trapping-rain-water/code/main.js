// O(n) time, O(1) space
function trap(height) {
    let left = 0;
    let right = height.length - 1;
    let leftMax = 0;           // tallest wall seen
    let rightMax = 0;
    let water = 0;
    while (left < right) {
        if (height[left] < height[right]) {
            const bar = height[left];
            leftMax = Math.max(leftMax, bar);
            water = water + leftMax - bar;
            left = left + 1;
        } else {
            const bar = height[right];
            rightMax = Math.max(rightMax, bar);
            water = water + rightMax - bar;
            right = right - 1;
        }
    }
    return water;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => trap(l.trim().split(/\s+/).map(Number))).join("\n"));
