function build(nums, i, picked, out) {
    if (i === nums.length) {
        out.push([...picked]); // a copy
    } else {
        picked.push(nums[i]); // pick
        build(nums, i + 1, picked, out);
        picked.pop(); // skip
        build(nums, i + 1, picked, out);
    }
}

function subsets(nums) {
    const out = [];
    build(nums, 0, [], out);
    return out;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => subsets(l.trim().split(" ").map(Number)).map(s => s.join(" ")).join(",")).join("\n"));
