function safe(queens, row, col) {
    for (let r = 0; r < row; r++) {
        const c = queens[r];
        const gap = row - r;
        if (col === c) {
            return false; // same column
        }
        if (col === c + gap || col === c - gap) {
            return false; // same diagonal
        }
    }
    return true;
}

function place(queens, row, n, out) {
    if (row === n) {
        out.push(queens.map(q => ".".repeat(q) + "Q" + ".".repeat(n - q - 1))); // a board drawn from queens
        return;
    }
    for (let col = 0; col < n; col++) {
        if (safe(queens, row, col)) {
            queens[row] = col; // a queen
            place(queens, row + 1, n, out);
        }
    }
}

function solveNQueens(n) {
    const out = [];
    place(new Array(n).fill(0), 0, n, out);
    return out;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    const p = l.split("|");
    if (p[0] === "N") return solveNQueens(Number(p[1])).map(b => b.join(",")).join("|");
    const q = p[1].trim() ? p[1].trim().split(" ").map(Number) : [];
    return String(safe(q, Number(p[2]), Number(p[3])));
}).join("\n"));
