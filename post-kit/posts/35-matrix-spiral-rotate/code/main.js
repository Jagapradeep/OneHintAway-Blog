function rotate(grid) {
    const n = grid.length;
    for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
            [grid[i][j], grid[j][i]] = [grid[j][i], grid[i][j]];
        }
    }
    for (const row of grid) {
        row.reverse();
    }
}

function spiralOrder(grid) {
    let top = 0;
    let bottom = grid.length - 1;
    let left = 0;
    let right = grid[0].length - 1;
    const result = [];
    while (top <= bottom && left <= right) {
        for (let col = left; col <= right; col++) {
            result.push(grid[top][col]);
        }
        top++;
        for (let row = top; row <= bottom; row++) {
            result.push(grid[row][right]);
        }
        right--;
        if (top > bottom || left > right) {
            return result; // nothing left
        }
        for (let col = right; col >= left; col--) {
            result.push(grid[bottom][col]);
        }
        bottom--;
        for (let row = bottom; row >= top; row--) {
            result.push(grid[row][left]);
        }
        left++;
    }
    return result;
}
// ---- test harness: not on the blog ----
const lines = require("fs").readFileSync(0, "utf8").split("\n").slice(0, -1);
console.log(lines.map(l => {
    const [h, rest] = l.split("|");
    const [m, n] = h.trim().split(" ").map(Number);
    const v = rest.trim().split(" ").map(Number);
    const g = [];
    for (let i = 0; i < m; i++) g.push(v.slice(i * n, (i + 1) * n));
    const s = spiralOrder(g).join(" ");
    return s + "|" + (m === n ? (rotate(g), g.flat().join(" ")) : "-");
}).join("\n"));
