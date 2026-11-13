// Search a sorted grid: read it as one long sorted row and binary search that (post 31).
// The reader types the numbers as one sorted list plus how many go in each row.
import type { Answer, Cell, Input, Pattern, Step } from "../schema.ts";
import { varOf } from "../schema.ts";
import { pick, sayOk, sortedOnly, step } from "./_lib.ts";

const pseudocode = [
  "function searchMatrix(grid, target):",
  "    cells = length(grid) * length(grid[0])",
  "    low = 0",
  "    high = cells - 1",
  "    while low <= high:",
  "        middle = floor((low + high) / 2)",
  "        if cell(grid, middle) == target:",
  "            return true",
  "        else if cell(grid, middle) < target:",
  "            low = middle + 1",
  "        else:",
  "            high = middle - 1",
  "    return false",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const cols = input.cols as number;
  const target = input.target as number;
  const n = nums.length;
  let low = 0, high = n - 1;
  let middle: number | "" = "";
  const snap = (line: number, say: string, focus = -1) => {
    const rows: Cell[][] = [];
    nums.forEach((v, k) => {
      if (k % cols === 0) rows.push([]);
      rows[rows.length - 1].push({ id: `c${k}`, v, state: k === focus ? "gold" : k < low || k > high ? "dim" : "plain" });
    });
    return step(line, say, [{ kind: "grid", id: "grid", label: "numbered row by row", rows }], { target, low, high, middle });
  };

  yield snap(3, `Read the grid as one sorted row of ${n} cells, numbered 0 to ${n - 1}.`);
  while (low <= high) {
    middle = Math.floor((low + high) / 2);
    const v = nums[middle];
    yield snap(5, `Cell ${middle} is row ${Math.floor(middle / cols)}, column ${middle % cols}. It holds ${v}.`, middle);
    if (v === target) {
      yield snap(7, `${v} is the target: return true.`, middle);
      return true;
    } else if (v < target) {
      low = middle + 1;
      yield snap(9, `${v} is less than ${target}: drop every cell up to ${middle}. low = ${low}.`);
    } else {
      high = middle - 1;
      yield snap(11, `${v} is more than ${target}: drop every cell from ${middle} on. high = ${high}.`);
    }
  }
  yield snap(12, `low has passed high: ${target} is not in the grid.`);
  return false;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const cols = input.cols as number;
  const target = input.target as number;
  const g = s.views[0];
  if (s.views.length !== 1 || g.kind !== "grid") return "needs exactly the grid view";
  const flat = g.rows.flat();
  if (g.rows.some((r, y) => r.length !== (y < g.rows.length - 1 ? cols : nums.length - cols * y))) return "every row holds cols cells";
  if (flat.length !== nums.length || flat.some((c, k) => c.v !== nums[k] || c.id !== `c${k}`)) return "the cells must be the input, row by row";
  const low = varOf(s, "low") as number, high = varOf(s, "high") as number;
  const middle = varOf(s, "middle");
  for (const [k, c] of flat.entries()) {
    const want = c.state === "gold" ? "gold" : k < low || k > high ? "dim" : "plain";
    if (c.state !== want || (c.state === "gold" && k !== middle)) return `cell ${k} is ${c.state}`;
  }
  // Everything dropped on the left is too small, everything dropped on the right too big.
  if (nums.slice(0, low).some((v) => v >= target) || nums.slice(high + 1).some((v) => v <= target)) return "a dropped cell could still hold the target";
  if (s.line === 5 && middle !== Math.floor((low + high) / 2)) return "middle is not the middle of low and high";
  if (s.line === 7 && nums[middle as number] !== target) return "'return true' without the target in the middle";
  if (isLast !== (s.line === 7 || s.line === 12) || (s.line === 12 && low <= high)) return "the trace must end on a return line";
  const m = typeof middle === "number" ? middle : 0;
  return sayOk(input, s, prev, [nums.length, nums.length - 1, Math.floor(m / cols), m % cols]);
}

export const search2dMatrix: Pattern = {
  id: "search-2d-matrix",
  title: "Search a 2D matrix",
  blurb: "A grid sorted row after row is one long sorted row in disguise: binary search it.",
  problem: "Say whether the target is in a grid whose rows continue one sorted list.",
  section: "Binary search",
  tier: "paid",
  pseudocode,
  fields: [
    { name: "nums", label: "Sorted numbers, row after row", kind: "ints", min: -99, max: 99, minLen: 1, maxLen: 12 },
    { name: "cols", label: "Per row", kind: "int", min: 1, max: 4 },
    { name: "target", label: "Target", kind: "int", min: -99, max: 99 },
  ],
  example: { nums: [1, 3, 5, 7, 9, 11], cols: 3, target: 11 },
  validate(input) {
    const nums = input.nums as number[];
    if (nums.length % (input.cols as number) !== 0) return `${nums.length} numbers can't fill rows of ${input.cols}.`;
    return sortedOnly("The numbers", nums);
  },
  random(rng) {
    const cols = pick(rng, 3, 4);
    const nums: number[] = [];
    let v = pick(rng, 1, 4);
    for (let k = cols * pick(rng, 2, 3); k > 0; k--) nums.push((v += pick(rng, 2, 4)));
    const hit = nums[pick(rng, 0, nums.length - 1)];
    return { nums, cols, target: rng() < 0.75 ? hit : hit + 1 };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => (a ? "The target is in the grid: true" : "The target is not in the grid: false"),
};
