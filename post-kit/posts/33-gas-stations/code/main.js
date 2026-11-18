function pumpsNeeded(stations, d) {
    let count = 0;
    for (let i = 1; i < stations.length; i++) {
        const gap = stations[i] - stations[i - 1];
        count += Math.ceil(gap / d) - 1;
    }
    return count;
}

function minMaxGap(stations, k) {
    const n = stations.length;
    let low = 0;
    let high = stations[n - 1] - stations[0];
    while (high - low > 0.000001) {
        const d = (low + high) / 2;
        if (pumpsNeeded(stations, d) <= k) {
            high = d; // fits: go lower
        } else {
            low = d; // too many: go higher
        }
    }
    return high;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => { const [k, rest] = l.split("|"); return minMaxGap(rest.trim().split(" ").map(Number), Number(k)).toFixed(2); }).join("\n"));
