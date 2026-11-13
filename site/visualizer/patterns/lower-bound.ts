// Lower bound: the first index whose number is not less than the target (post 29).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf, varOf } from "../schema.ts";
import { arr, pick, ptrs, sayOk, sortedOnly, step, tiles } from "./_lib.ts";

const pseudocode = [
  "function lowerBound(nums, target):",
  "    low = 0",
  "    high = length(nums)   // one past the end",
  "    while low < high:",
  "        middle = floor((low + high) / 2)",
  "        if nums[middle] < target:",
  "            low = middle + 1",
  "        else:",
  "            high = middle   // may be it",
  "    return low",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const target = input.target as number;
  const n = nums.length;
  let low = 0, high = n;
  let middle: number | "" = "";
  const snap = (line: number, say: string, focus = -1) =>
    step(
      line,
      say,
      [arr("nums", tiles(nums), (k) => (k === focus ? "gold" : k < low || k >= high ? "dim" : "plain"), ptrs(n, middle === "" ? {} : { middle }), { window: { lo: low, hi: high - 1 } })],
      { target, low, high, middle },
    );

  yield snap(2, `high starts one past the end, at ${n}: the answer can be "after every number".`);
  while (low < high) {
    middle = Math.floor((low + high) / 2);
    const v = nums[middle];
    yield snap(4, `The middle of ${low} and ${high} is index ${middle}. It holds ${v}.`, middle);
    if (v < target) {
      low = middle + 1;
      yield snap(6, `${v} is less than ${target}: the answer is further right. low = ${low}.`);
    } else {
      high = middle;
      yield snap(8, `${v} is not less than ${target}: index ${middle} may be the answer, so high = ${high}.`);
    }
  }
  yield snap(9, low < n ? `low and high meet at index ${low}: the first number that is not less than ${target}.` : `low and high meet at ${low}, past the end: every number is less than ${target}.`, low);
  return low;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const target = input.target as number;
  const a = arrayOf(s, "nums");
  if (!a?.window || s.views.length !== 1) return "needs exactly the array view nums, with a window";
  if (a.cells.some((c, i) => c.v !== nums[i] || c.id !== `c${i}`)) return "the cells must stay as the input";
  const low = varOf(s, "low") as number, high = varOf(s, "high") as number;
  if (a.window.lo !== low || a.window.hi !== high - 1) return "the window must frame low up to high - 1";
  if (!(0 <= low && low <= high && high <= nums.length)) return `low ${low} and high ${high} are out of order`;
  // What makes the answer safe: everything before low is too small, everything from high on is not.
  if (nums.slice(0, low).some((v) => v >= target)) return "a number before low is not less than the target";
  if (nums.slice(high).some((v) => v < target)) return "a number from high on is less than the target";
  const middle = varOf(s, "middle");
  if (s.line === 4 && middle !== Math.floor((low + high) / 2)) return "middle is not the middle of low and high";
  if (isLast !== (s.line === 9) || (isLast && low !== high)) return "the trace must end on 'return low', when low meets high";
  return sayOk(input, s, prev);
}

export const lowerBound: Pattern = {
  id: "lower-bound",
  title: "Lower bound",
  blurb: "Not 'is it there' but 'where does it start': binary search that keeps the middle as a maybe.",
  problem: "Find the first index whose number is not less than the target.",
  section: "Binary search",
  tier: "paid",
  pseudocode,
  fields: [
    { name: "nums", label: "Sorted numbers", kind: "ints", min: -99, max: 99, minLen: 1, maxLen: 10 },
    { name: "target", label: "Target", kind: "int", min: -99, max: 99 },
  ],
  example: { nums: [1, 2, 2, 2, 4, 5], target: 2 },
  validate: (input) => sortedOnly("The numbers", input.nums as number[]),
  random(rng) {
    const nums: number[] = [];
    let v = pick(rng, 1, 4);
    for (let k = pick(rng, 6, 10); k > 0; k--) nums.push((v += pick(rng, 0, 3)));
    return { nums, target: pick(rng, nums[0] - 1, nums[nums.length - 1] + 1) };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => `The first index not less than the target: ${a}`,
};
