// Bubble sort: swap neighbours that are out of order, sweep after sweep (post 24).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf } from "../schema.ts";
import { arr, ascending, eq, list, pick, ptrs, sayOk, sortedCopy, step, swap, tiles, vals } from "./_lib.ts";

const pseudocode = [
  "function bubbleSort(nums):",
  "    n = length(nums)",
  "    for sweep from 1 to n - 1:",
  "        swapped = false",
  "        for j from 0 to n - 1 - sweep:",
  "            if nums[j] > nums[j + 1]:",
  "                swap nums[j], nums[j + 1]",
  "                swapped = true",
  "        if not swapped:",
  "            return nums   // already sorted",
  "    return nums",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const t = tiles(input.nums as number[]);
  const n = t.length;
  let settled = 0; // how many numbers at the right end are in their final place
  const snap = (line: number, say: string, j: number, sweep: number | "", swapped: string) =>
    step(line, say, [arr("nums", t, (k) => (k >= n - settled ? "steel" : k === j || k === j + 1 ? "gold" : "plain"), ptrs(n, { j }))], { sweep, swapped });

  for (let sweep = 1; sweep <= n - 1; sweep++) {
    let swapped = false;
    yield snap(3, `Sweep ${sweep}: walk left to right and swap any two neighbours that are out of order.`, -2, sweep, "false");
    for (let j = 0; j <= n - 1 - sweep; j++) {
      if (t[j].v > t[j + 1].v) {
        swap(t, j, j + 1);
        swapped = true;
        yield snap(6, `${t[j + 1].v} is bigger than ${t[j].v}: swap them.`, j, sweep, "true");
      } else {
        yield snap(5, `${t[j].v} and ${t[j + 1].v} are in order: no swap.`, j, sweep, String(swapped));
      }
    }
    settled = sweep;
    if (!swapped) {
      settled = n;
      yield snap(9, "A whole sweep without a swap: the row is already sorted. Stop early.", -2, sweep, "false");
      return t.map((x) => x.v as number);
    }
  }
  settled = n;
  yield snap(10, "Every sweep is done: sorted.", -2, "", "");
  return t.map((x) => x.v as number);
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const a = arrayOf(s, "nums");
  if (!a || s.views.length !== 1) return "needs exactly the array view nums";
  const now = vals(s, "nums");
  if (!eq(sortedCopy(now), sortedCopy(nums))) return "the cells are not the input's numbers";
  // Settled cells form the right end, and hold the largest numbers in order.
  const first = a.cells.findIndex((c) => c.state === "steel");
  if (first >= 0) {
    if (a.cells.slice(first).some((c) => c.state !== "steel")) return "settled cells must be the right end";
    if (!eq(now.slice(first), sortedCopy(nums).slice(first))) return "a settled cell is not in its final place";
  }
  if (isLast !== (s.line === 9 || s.line === 10)) return "the trace must end on a return line";
  if (isLast && (!ascending(now) || first !== 0)) return "the trace ends before the row is sorted";
  return sayOk(input, s, prev);
}

export const bubbleSort: Pattern = {
  id: "bubble-sort",
  title: "Bubble sort",
  blurb: "Swap neighbours that are out of order; each sweep carries the biggest number left to the end.",
  problem: "Sort the numbers from small to large.",
  section: "Recursion and sorting",
  tier: "free",
  post: "bubble-sort",
  pseudocode,
  fields: [{ name: "nums", label: "Numbers", kind: "ints", min: -20, max: 99, minLen: 1, maxLen: 7 }],
  example: { nums: [5, 1, 4, 2, 8] },
  validate: () => null,
  random: (rng) => ({ nums: list(rng, pick(rng, 4, 6), 1, 30) }),
  run,
  check,
  sameAnswer: (_i, got, expected) => eq(got, expected),
  answerText: (a) => `Sorted: ${(a as number[]).join(", ")}`,
};
