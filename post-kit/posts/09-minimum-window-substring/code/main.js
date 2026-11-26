// O(m + n) time, O(k) space
var minWindow = function (s, t) {
    const need = new Map();
    for (const c of t) {
        need.set(c, (need.get(c) ?? 0) + 1);
    }
    let missing = t.length;
    let left = 0;
    let bestStart = 0;
    let bestLen = Infinity;
    for (let right = 0; right < s.length; right++) {
        const c = s[right];
        if ((need.get(c) ?? 0) > 0) {
            missing = missing - 1;
        }
        need.set(c, (need.get(c) ?? 0) - 1);
        while (missing === 0) {
            if (right - left + 1 < bestLen) {
                bestStart = left;
                bestLen = right - left + 1;
            }
            const d = s[left];
            need.set(d, need.get(d) + 1);
            if (need.get(d) > 0) {
                missing = missing + 1;
            }
            left = left + 1;
        }
    }
    if (bestLen === Infinity) {
        return "";
    }
    return s.substring(bestStart, bestStart + bestLen);
};
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => { const [s, t] = l.split(" "); return minWindow(s, t) || "-"; }).join("\n"));
