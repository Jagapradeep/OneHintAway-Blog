// O(n) time, O(n) stack space. BigInt keeps the answer exact past 2^53.
function factorial(n) {
    if (n === 0n) {
        return 1n;               // base case
    }
    return n * factorial(n - 1n);
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => factorial(BigInt(l.trim())).toString()).join("\n"));
