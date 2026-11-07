function searchMatrix(grid, target) {
    const cells = grid.length * grid[0].length;
    let low = 0;
    let high = cells - 1;
    while (low <= high) {
        const middle = Math.floor((low + high) / 2);
        if (cell(grid, middle) === target) {
            return true;
        } else if (cell(grid, middle) < target) {
            low = middle + 1;
        } else {
            high = middle - 1;
        }
    }
    return false;
}

// index i of the grid read row after row
function cell(grid, i) {
    const cols = grid[0].length;
    const row = Math.floor(i / cols);
    const col = i % cols;
    return grid[row][col];
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    const [t, rc, rest] = l.split("|");
    const [r, c] = rc.trim().split(" ").map(Number);
    const v = rest.trim().split(" ").map(Number);
    const g = [];
    for (let i = 0; i < r; i++) g.push(v.slice(i * c, (i + 1) * c));
    return searchMatrix(g, Number(t)) ? "true" : "false";
}).join("\n"));
