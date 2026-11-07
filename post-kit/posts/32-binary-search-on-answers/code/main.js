function minSpeed(piles, hours) {
    let low = 1;
    let high = Math.max(...piles);
    while (low < high) {
        const speed = Math.floor((low + high) / 2);
        if (hoursAt(piles, speed) <= hours) {
            high = speed; // fast enough
        } else {
            low = speed + 1; // too slow
        }
    }
    return low;
}

function hoursAt(piles, speed) {
    let total = 0;
    for (const pile of piles) {
        total += Math.ceil(pile / speed);
    }
    return total;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    const [h, rest] = l.split("|");
    return minSpeed(rest.trim().split(" ").map(Number), Number(h));
}).join("\n"));
