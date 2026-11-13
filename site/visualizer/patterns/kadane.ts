// Kadane's algorithm: the largest sum of numbers in a row (LeetCode 53, post 12).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf, varOf } from "../schema.ts";
import { arr, list, pick, ptrs, sayOk, step, sum, tiles } from "./_lib.ts";

const pseudocode = [
  "function maxSubArray(nums):",
  "    current = 0          // sum so far",
  "    best = nums[0]       // largest so far",
  "    for each x in nums:",
  "        if current < 0:  // in debt?",
  "            current = 0  // start fresh",
  "        current = current + x",
  "        best = max(best, current)",
  "    return best",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const n = nums.length;
  let current = 0, best = nums[0], lo = 0, hi = -1;
  const snap = (line: number, say: string, focus = -1) =>
    step(line, say, [arr("nums", tiles(nums), (i) => (i === focus ? "gold" : i >= lo && i <= hi ? "plain" : "dim"), ptrs(n, { x: focus }), { window: { lo, hi } })], { current, best });

  yield snap(2, `current starts at 0. best starts as the first number, ${best}.`);
  for (let i = 0; i < n; i++) {
    const x = nums[i];
    if (current < 0) {
      const debt = current;
      current = 0;
      lo = i;
      hi = i - 1;
      yield snap(5, `current is ${debt}: a debt. Drop that run and start fresh at ${x}.`, i);
    }
    current += x;
    hi = i;
    yield snap(6, `Add ${x}: current = ${current}.`, i);
    const old = best;
    best = Math.max(best, current);
    yield snap(7, current > old ? `${current} beats ${old}: best = ${best}.` : `${current} does not beat ${old}: best stays ${best}.`, i);
  }
  yield snap(8, `Done. The largest sum of numbers in a row is ${best}.`);
  return best;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const a = arrayOf(s, "nums");
  if (!a?.window || s.views.length !== 1) return "needs exactly the array view nums, with a window";
  const { lo, hi } = a.window;
  if (a.cells.some((c, i) => c.v !== nums[i] || c.id !== `c${i}`)) return "the cells must stay as the input";
  const current = varOf(s, "current");
  if (current !== sum(nums.slice(lo, hi + 1))) return `current ${current} is not the sum of the window`;
  // best = the largest run that ends at or before the last number counted (the newest one only after 'best = max').
  const lastEnd = s.line === 6 ? hi - 1 : hi;
  let want = nums[0];
  for (let e = 0; e <= lastEnd; e++) for (let b = 0; b <= e; b++) want = Math.max(want, sum(nums.slice(b, e + 1)));
  if (varOf(s, "best") !== want) return `best is ${varOf(s, "best")}, the largest run so far is ${want}`;
  if (isLast !== (s.line === 8) || (isLast && hi !== nums.length - 1)) return "the trace must end on 'return best', after the last number";
  return sayOk(input, s, prev);
}

export const kadane: Pattern = {
  id: "kadane",
  title: "Kadane's algorithm",
  blurb: "The largest sum of numbers in a row: drop the running sum the moment it goes below zero.",
  problem: "Find the largest sum of numbers in a row.",
  section: "Arrays and hashing",
  tier: "paid",
  post: "kadane",
  pseudocode,
  fields: [{ name: "nums", label: "Numbers", kind: "ints", min: -50, max: 50, minLen: 1, maxLen: 8 }],
  example: { nums: [4, -6, 3, -1, 5, -9, 2] },
  validate: () => null,
  random: (rng) => ({ nums: list(rng, pick(rng, 5, 8), -9, 9) }),
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => `Largest sum of numbers in a row: ${a}`,
};
