function permute(nums, used, path, out) {
    if (path.length === nums.length) {
        out.push([...path]);
        return out;
    }
    for (let i = 0; i < nums.length; i++) {
        if (!used[i]) {
            used[i] = true; // choose
            path.push(nums[i]);
            permute(nums, used, path, out);
            path.pop(); // undo
            used[i] = false;
        }
    }
    return out;
}

function find(nums, i, left, path, out) {
    if (left === 0) {
        out.push([...path]);
        return out;
    }
    for (let j = i; j < nums.length; j++) {
        if (nums[j] <= left) {
            path.push(nums[j]); // choose
            const rest = left - nums[j];
            find(nums, j, rest, path, out);
            path.pop(); // undo
        }
    }
    return out;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    const p = l.split("|");
    const res = p[0] === "P"
        ? (nums => permute(nums, nums.map(() => false), [], []))(p[1].trim().split(" ").map(Number))
        : find(p[2].trim().split(" ").map(Number), 0, Number(p[1]), [], []);
    return res.map(s => s.join(" ")).join(",");
}).join("\n"));
