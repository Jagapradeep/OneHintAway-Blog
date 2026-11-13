// Selection sort: find the smallest number left and swap it into the next spot (post 23).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf } from "../schema.ts";
import { arr, ascending, eq, list, pick, ptrs, sayOk, sortedCopy, step, swap, tiles, vals } from "./_lib.ts";

const pseudocode = [
  "function selectionSort(nums):",
  "    n = length(nums)",
  "    for i from 0 to n - 2:",
  "        smallest = i   // an index",
  "        for j from i + 1 to n - 1:",
  "            if nums[j] < nums[smallest]:",
  "                smallest = j",
  "        swap nums[i], nums[smallest]",
  "    return nums",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const t = tiles(input.row as number[]);
  const n = t.length;
  // Cells before `done` are settled.
  const snap = (line: number, say: string, done: number, i: number, j: number, smallest: number) =>
    step(line, say, [arr("row", t, (k) => (k < done ? "steel" : k === smallest ? "gold" : "plain"), ptrs(n, { i, smallest, j }))]);

  for (let i = 0; i < n - 1; i++) {
    let smallest = i;
    yield snap(3, `Spot ${i} needs the smallest number left. Start by remembering ${t[i].v}.`, i, i, -1, smallest);
    for (let j = i + 1; j < n; j++) {
      if (t[j].v < t[smallest].v) {
        const old = t[smallest].v;
        smallest = j;
        yield snap(6, `${t[j].v} is smaller than ${old}: remember it instead.`, i, i, j, smallest);
      } else {
        yield snap(5, `${t[j].v} is not smaller than ${t[smallest].v}: keep ${t[smallest].v}.`, i, i, j, smallest);
      }
    }
    const stays = smallest === i;
    swap(t, i, smallest);
    yield snap(7, stays ? `${t[i].v} is already in spot ${i}: it swaps with itself.` : `Swap ${t[i].v} into spot ${i}.`, i + 1, -1, -1, -1);
  }
  yield snap(8, "One number is left, the largest, and it is already last: sorted.", n, -1, -1, -1);
  return t.map((x) => x.v as number);
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const row = input.row as number[];
  const a = arrayOf(s, "row");
  if (!a || s.views.length !== 1) return "needs exactly the array view row";
  const now = vals(s, "row");
  if (!eq(sortedCopy(now), sortedCopy(row))) return "the cells are not the input's numbers";
  // Settled cells are the left end and hold the smallest numbers in order.
  const done = a.cells.filter((c) => c.state === "steel").length;
  if (a.cells.slice(0, done).some((c) => c.state !== "steel")) return "settled cells must be the left end";
  if (!eq(now.slice(0, done), sortedCopy(row).slice(0, done))) return "a settled cell is not in its final place";
  const at = (id: string) => a.pointers.find((p) => p.id === id)?.at;
  const i = at("i"), j = at("j"), smallest = at("smallest");
  if (smallest !== undefined && i !== undefined) {
    const seen = now.slice(i, (j ?? i) + 1);
    if (now[smallest] !== Math.min(...seen) || smallest < i) return "smallest must point at the smallest number looked at so far";
  }
  if (isLast !== (s.line === 8)) return "the trace must end on 'return nums'";
  if (isLast && (!ascending(now) || done !== row.length)) return "the trace ends before the row is sorted";
  return sayOk(input, s, prev);
}

export const selectionSort: Pattern = {
  id: "selection-sort",
  title: "Selection sort",
  blurb: "Find the smallest number left, swap it into the next spot, repeat.",
  problem: "Sort the numbers from small to large.",
  section: "Recursion and sorting",
  tier: "paid",
  post: "selection-sort",
  pseudocode,
  fields: [{ name: "row", label: "Numbers", kind: "ints", min: -20, max: 99, minLen: 1, maxLen: 6 }],
  example: { row: [5, 2, 8, 1, 4] },
  validate: () => null,
  random: (rng) => ({ row: list(rng, pick(rng, 4, 6), 1, 30) }),
  run,
  check,
  sameAnswer: (_i, got, expected) => eq(got, expected),
  answerText: (a) => `Sorted: ${(a as number[]).join(", ")}`,
};
