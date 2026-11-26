function countPrimes(n) {
    if (n < 3) {                // only 0 and 1 are below n
        return 0;
    }
    const isPrime = new Array(n).fill(true);
    isPrime[0] = false;
    isPrime[1] = false;
    let p = 2;
    while (p * p < n) {
        if (isPrime[p]) {
            let m = p * p;
            while (m < n) {
                isPrime[m] = false;
                m = m + p;
            }
        }
        p = p + 1;
    }
    return isPrime.filter(Boolean).length;
}

function gcd(a, b) {
    while (b !== 0) {
        const remainder = a % b;
        a = b;
        b = remainder;
    }
    return a;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => { const w = l.trim().split(/\s+/); return w[0] === "primes" ? countPrimes(Number(w[1])) : gcd(Number(w[1]), Number(w[2])); }).join("\n"));
