// Spiral order: four walls that move in after each side is read (post 35). The
// post's pseudocode also holds rotate(); the player walks spiralOrder, the post's
// first worked example. The reader types the numbers row after row plus the row length.
import type { Answer, ArrayView, Cell, GridView, Input, Pattern, Step } from "../schema.ts";
import { varOf } from "../schema.ts";
import { arr, list, pick, sayOk, spaced, step, tiles } from "./_lib.ts";

const pseudocode = [
  "function rotate(grid):",
  "    n = length(grid)",
  "    for i from 0 to n - 1:",
  "        for j from i + 1 to n - 1:",
  "            swap grid[i][j], grid[j][i]",
  "    for each row in grid:",
  "        reverse row",
  "",
  "function spiralOrder(grid):",
  "    top = 0",
  "    bottom = length(grid) - 1",
  "    left = 0",
  "    right = length(grid[0]) - 1",
  "    result = empty list",
  "    while top <= bottom and left <= right:",
  "        for col from left to right:",
  "            add grid[top][col] to result",
  "        top = top + 1   // wall moves in",
  "        for row from top to bottom:",
  "            add grid[row][right] to result",
  "        right = right - 1   // wall in",
  "",
  "        if top > bottom or left > right:",
  "            return result   // nothing left",
  "        for col from right down to left:",
  "            add grid[bottom][col] to result",
  "        bottom = bottom - 1",
  "        for row from bottom down to top:",
  "            add grid[row][left] to result",
  "        left = left + 1",
  "    return result",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const cols = input.cols as number;
  const rows = nums.length / cols;
  const at = (r: number, c: number) => nums[r * cols + c];
  let top = 0, bottom = rows - 1, left = 0, right = cols - 1;
  const read = new Set<number>(); // cell numbers already added
  const result: number[] = [];
  let focus = -1;
  const snap = (line: number, say: string) => {
    const g: Cell[][] = [];
    for (let r = 0; r < rows; r++) g.push(Array.from({ length: cols }, (_, c) => {
      const k = r * cols + c;
      return { id: `c${k}`, v: nums[k], state: k === focus ? "gold" : read.has(k) ? "steel" : "plain" };
    }));
    const out = tiles(nums.map((_, k) => (k < result.length ? result[k] : "")));
    return step(line, say, [
      { kind: "grid", id: "grid", label: "Grid", rows: g },
      arr("result", out, (k) => (k === result.length - 1 && focus >= 0 ? "gold" : "plain"), [], { label: "Result", hideIndex: true }),
    ], { top, bottom, left, right });
  };
  const add = (r: number, c: number, side: string) => {
    focus = r * cols + c;
    read.add(focus);
    result.push(at(r, c));
    return snap(side === "top" || side === "bottom" ? (side === "top" ? 16 : 25) : side === "right" ? 19 : 28, `${side[0].toUpperCase()}${side.slice(1)}: add ${at(r, c)} from row ${r}, column ${c}.`);
  };

  yield snap(12, `Four walls around the grid: top = 0, bottom = ${bottom}, left = 0, right = ${right}.`);
  while (top <= bottom && left <= right) {
    for (let c = left; c <= right; c++) yield add(top, c, "top");
    top++;
    focus = -1;
    yield snap(17, `The top row is read: top moves in to ${top}.`);
    for (let r = top; r <= bottom; r++) yield add(r, right, "right");
    right--;
    focus = -1;
    yield snap(20, `The right side is read: right moves in to ${right}.`);
    if (top > bottom || left > right) {
      yield snap(23, `${top > bottom ? `top = ${top} is past bottom = ${bottom}` : `left = ${left} is past right = ${right}`}: nothing is left. Return.`);
      return result;
    }
    for (let c = right; c >= left; c--) yield add(bottom, c, "bottom");
    bottom--;
    focus = -1;
    yield snap(26, `The bottom row is read: bottom moves up to ${bottom}.`);
    for (let r = bottom; r >= top; r--) yield add(r, left, "left");
    left++;
    focus = -1;
    yield snap(29, `The left side is read: left moves in to ${left}.`);
  }
  yield snap(30, `The walls have crossed: every value is read. Return ${spaced(result)}.`);
  return result;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const cols = input.cols as number;
  const g = s.views[0] as GridView, out = s.views[1] as ArrayView;
  if (s.views.length !== 2 || g.kind !== "grid" || out.kind !== "array") return "needs the grid and the result row";
  const flat = g.rows.flat();
  if (g.rows.some((r) => r.length !== cols) || flat.length !== nums.length || flat.some((c, k) => c.v !== nums[k])) return "the grid must be the input, row by row";
  const top = varOf(s, "top") as number, bottom = varOf(s, "bottom") as number;
  const left = varOf(s, "left") as number, right = varOf(s, "right") as number;
  const res = out.cells.filter((c) => c.v !== "").map((c) => c.v as number);
  if (out.cells.some((c, k) => (c.v === "") !== (k >= res.length))) return "the result fills from the left with no gaps";
  // Read cells are exactly those outside the walls, plus the part of the current side done so far.
  const lit = flat.flatMap((c, k) => (c.state === "plain" ? [] : [k]));
  if (lit.length !== res.length) return `${lit.length} cells are lit, the result holds ${res.length}`;
  const inside = (k: number) => {
    const r = Math.floor(k / cols), c = k % cols;
    return r >= top && r <= bottom && c >= left && c <= right;
  };
  const outside = flat.filter((_, k) => !inside(k)).length;
  if (lit.filter((k) => !inside(k)).length !== outside) return "every cell outside the walls must be read";
  if (res.length - outside > Math.max(cols, nums.length / cols)) return "only one side may be part read";
  // Each value enters the result once, and the result is made of read cells.
  const want = [...res].sort((x, y) => x - y).join();
  if (lit.map((k) => nums[k]).sort((x, y) => x - y).join() !== want) return "the result must hold the values of the lit cells";
  const gold = flat.filter((c) => c.state === "gold").length;
  if (gold > 1 || (gold === 1) !== [16, 19, 25, 28].includes(s.line)) return "exactly the newly added cell is gold";
  if (prev && res.length < (prev.views[1] as ArrayView).cells.filter((c) => c.v !== "").length) return "the result never shrinks";
  if (isLast !== (s.line === 23 || s.line === 30) || (isLast && res.length !== nums.length)) return "the trace ends on a return line with every value read";
  return sayOk(input, s, prev);
}

export const spiralMatrix: Pattern = {
  id: "spiral-matrix",
  title: "Spiral order",
  blurb: "Four walls move in after each side: read a grid from the outside in.",
  problem: "Read every value of the grid in spiral order, starting at the top left.",
  section: "2D arrays and strings",
  tier: "free",
  pseudocode,
  fields: [
    { name: "nums", label: "Numbers, row after row", kind: "ints", min: -99, max: 99, minLen: 1, maxLen: 12 },
    { name: "cols", label: "Per row", kind: "int", min: 1, max: 4 },
  ],
  example: { nums: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], cols: 4 },
  validate(input) {
    const n = (input.nums as number[]).length;
    const cols = input.cols as number;
    if (n % cols !== 0) return `${n} numbers can't fill rows of ${cols}.`;
    return n / cols > 4 ? "At most 4 rows: use fewer numbers or a longer row." : null;
  },
  random(rng) {
    const cols = pick(rng, 2, 4);
    const rows = pick(rng, 2, Math.min(4, Math.floor(12 / cols)));
    return { nums: list(rng, rows * cols, 1, 30), cols };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => JSON.stringify(got) === JSON.stringify(expected),
  answerText: (a) => `Spiral order: ${spaced(a as number[])}`,
};
