const MOVES = [[1, 0], [-1, 0], [0, 1], [0, -1]]; // down, up, right, left

function walk(grid, word, row, col, i) {
    if (grid[row][col] !== word[i]) {
        return false;
    }
    if (i === word.length - 1) {
        return true;
    }
    grid[row][col] = "#"; // in use
    for (const [dr, dc] of MOVES) { // each cell next to [row, col]
        const r = row + dr, c = col + dc;
        if (r >= 0 && r < grid.length && c >= 0 && c < grid[0].length) {
            if (walk(grid, word, r, c, i + 1)) {
                return true;
            }
        }
    }
    grid[row][col] = word[i]; // undo
    return false;
}

function exist(grid, word) {
    for (let row = 0; row < grid.length; row++) {
        for (let col = 0; col < grid[0].length; col++) {
            if (walk(grid, word, row, col, 0)) {
                return true;
            }
        }
    }
    return false;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => { const [w, rows] = l.split("|"); return exist(rows.split("/").map(r => r.split("")), w); }).join("\n"));
