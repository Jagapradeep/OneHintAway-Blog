// O(log n) time, O(1) space. x, n and m are BigInt values so the products stay exact.
function power(x, n, m) {
    let answer = 1n % m;
    let block = x % m;
    while (n > 0n) {
        if (n % 2n === 1n) {
            answer = (answer * block) % m;
        }
        block = (block * block) % m;
        n = n / 2n;
    }
    return answer;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => { const [x, n, m] = l.trim().split(/\s+/).map(BigInt); return power(x, n, m).toString(); }).join("\n"));
