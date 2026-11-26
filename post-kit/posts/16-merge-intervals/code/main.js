// O(n log n) time for the sort, O(n) space for the result
function merge(intervals) {
    intervals.sort((a, b) => a[0] - b[0]);
    const merged = [];
    merged.push([intervals[0][0], intervals[0][1]]);
    for (let i = 1; i < intervals.length; i++) {
        const [start, end] = intervals[i];
        const last = merged[merged.length - 1];
        if (start <= last[1]) {             // overlap
            last[1] = Math.max(last[1], end);
        } else {
            merged.push([start, end]);
        }
    }
    return merged;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => merge(l.split(",").map(p => p.trim().split(/\s+/).map(Number))).map(p => p.join(" ")).join(", ")).join("\n"));
