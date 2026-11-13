// Sliding window of a fixed size: the largest sum of k numbers in a row (post 07).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf, varOf } from "../schema.ts";
import { arr, list, pick, sayOk, step, sum, tiles } from "./_lib.ts";

const pseudocode = [
  "function maxSum(nums, k):",
  "    total = 0",
  "    for i from 0 to k - 1:",
  "        total = total + nums[i]",
  "    best = total",
  "    for i from k to length(nums) - 1:",
  "        total = total + nums[i] - nums[i - k]",
  "        best = max(best, total)",
  "    return best",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const k = input.k as number;
  let total = 0, lo = 0, hi = -1;
  let best: number | "" = "";
  const snap = (line: number, say: string, focus = -1, gone = -1) =>
    step(line, say, [arr("nums", tiles(nums), (i) => (i === focus ? "gold" : i === gone ? "steel" : i >= lo && i <= hi ? "plain" : "dim"), [], { window: { lo, hi } })], { k, total, best });

  yield snap(1, `The window will hold ${k} numbers in a row. total starts at 0.`);
  for (let i = 0; i < k; i++) {
    total += nums[i];
    hi = i;
    yield snap(3, `Add ${nums[i]} to fill the window: total = ${total}.`, i);
  }
  best = total;
  yield snap(4, `The first window is full. best = ${best}.`);
  for (let i = k; i < nums.length; i++) {
    total += nums[i] - nums[i - k];
    lo = i - k + 1;
    hi = i;
    yield snap(6, `Slide one step: add ${nums[i]}, drop ${nums[i - k]}. total = ${total}.`, i, i - k);
    const old: number = best;
    best = Math.max(old, total);
    yield snap(7, total > old ? `${total} beats ${old}: best = ${best}.` : `${total} does not beat ${old}: best stays ${best}.`);
  }
  yield snap(8, `Every window is checked. The largest sum is ${best}.`);
  return best;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const k = input.k as number;
  const a = arrayOf(s, "nums");
  if (!a?.window || s.views.length !== 1) return "needs exactly the array view nums, with a window";
  const { lo, hi } = a.window;
  if (a.cells.some((c, i) => c.v !== nums[i] || c.id !== `c${i}`)) return "the cells must stay as the input";
  if (hi - lo + 1 > k) return `the window holds ${hi - lo + 1} numbers, more than k`;
  if (varOf(s, "total") !== sum(nums.slice(lo, hi + 1))) return `total ${varOf(s, "total")} is not the sum of the window`;
  const best = varOf(s, "best");
  if ((best === "") !== s.line < 4) return "best is set exactly when the first window is full";
  if (best !== "") {
    // The best of every full window seen so far; on the "slide" line the new one is not counted yet.
    const lastEnd = s.line === 6 ? hi - 1 : hi;
    let want = -Infinity;
    for (let e = k - 1; e <= lastEnd; e++) want = Math.max(want, sum(nums.slice(e - k + 1, e + 1)));
    if (best !== want) return `best is ${best}, the largest full window so far is ${want}`;
  }
  if (isLast !== (s.line === 8) || (isLast && hi !== nums.length - 1)) return "the trace must end on 'return best', after the last window";
  return sayOk(input, s, prev);
}

export const fixedWindow: Pattern = {
  id: "fixed-window",
  title: "Sliding window, fixed size",
  blurb: "The best run of exactly k numbers: slide the window, add one, drop one.",
  problem: "Find the largest sum of k numbers in a row.",
  section: "Arrays and hashing",
  tier: "paid",
  post: "sliding-window-fixed-size",
  pseudocode,
  fields: [
    { name: "nums", label: "Numbers", kind: "ints", min: -20, max: 50, minLen: 1, maxLen: 10 },
    { name: "k", label: "Window size k", kind: "int", min: 1, max: 10 },
  ],
  example: { nums: [2, 1, 5, 1, 3, 2], k: 3 },
  validate: (input) => ((input.k as number) > (input.nums as number[]).length ? "k can't be larger than the count of numbers." : null),
  random(rng) {
    const n = pick(rng, 5, 9);
    return { nums: list(rng, n, -5, 20), k: pick(rng, 2, 4) };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => `Largest sum of k numbers in a row: ${a}`,
};
