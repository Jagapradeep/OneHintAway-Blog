function edge(nums, k, empty) {
    if (k < 0 || k >= nums.length) {
        return empty;
    }
    return nums[k];
}

function median(a, b) {
    if (a.length > b.length) {
        return median(b, a); // a: shorter
    }
    const m = a.length;
    const n = b.length;
    const half = Math.floor((m + n + 1) / 2);
    let low = 0;
    let high = m;
    while (low < high) {
        const i = Math.floor((low + high) / 2);
        if (b[half - i - 1] > a[i]) {
            low = i + 1; // more from a
        } else {
            high = i;
        }
    }
    const j = half - low; // low = the cut in a
    const leftA = edge(a, low - 1, -Infinity);
    const leftB = edge(b, j - 1, -Infinity);
    const leftMax = Math.max(leftA, leftB);
    if ((m + n) % 2 === 1) {
        return leftMax;
    }
    const rightA = edge(a, low, Infinity);
    const rightB = edge(b, j, Infinity);
    const rightMin = Math.min(rightA, rightB);
    return (leftMax + rightMin) / 2;
}
// ---- test harness: not on the blog ----
const parse = s => s.trim() ? s.trim().split(" ").map(Number) : [];
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => { const [x, y] = l.split("|"); return median(parse(x), parse(y)).toFixed(1); }).join("\n"));
