// Smallest number in a rotated sorted array: binary search on which half is broken (post 30).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf, varOf } from "../schema.ts";
import { arr, pick, ptrs, sayOk, step, tiles } from "./_lib.ts";

const pseudocode = [
  "function findMin(nums):",
  "    low = 0",
  "    high = length(nums) - 1",
  "    while low < high:",
  "        middle = floor((low + high) / 2)",
  "        if nums[middle] > nums[high]:",
  "            low = middle + 1",
  "        else:",
  "            high = middle",
  "    return nums[low]",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const n = nums.length;
  let low = 0, high = n - 1;
  let middle: number | "" = "";
  const snap = (line: number, say: string, gold: number[] = []) =>
    step(
      line,
      say,
      [arr("nums", tiles(nums), (k) => (gold.includes(k) ? "gold" : k < low || k > high ? "dim" : "plain"), ptrs(n, middle === "" ? {} : { middle }), { window: { lo: low, hi: high } })],
      { low, high, middle },
    );

  yield snap(2, "The smallest number sits where the climbing order breaks. low and high start at the two ends.");
  while (low < high) {
    middle = Math.floor((low + high) / 2);
    const m = nums[middle], end = nums[high];
    yield snap(4, `Index ${middle} holds ${m}. Compare it with the right end of the range, ${end}.`, [middle, high]);
    if (m > end) {
      low = middle + 1;
      yield snap(6, `${m} is bigger than ${end}: the break is to the right of the middle. low = ${low}.`);
    } else {
      high = middle;
      yield snap(8, `${m} is not bigger than ${end}: the smallest is the middle or left of it. high = ${high}.`);
    }
  }
  yield snap(9, `low and high meet at index ${low}: the smallest number is ${nums[low]}.`, [low]);
  return nums[low];
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const a = arrayOf(s, "nums");
  if (!a?.window || s.views.length !== 1) return "needs exactly the array view nums, with a window";
  if (a.cells.some((c, i) => c.v !== nums[i] || c.id !== `c${i}`)) return "the cells must stay as the input";
  const low = varOf(s, "low") as number, high = varOf(s, "high") as number;
  if (a.window.lo !== low || a.window.hi !== high) return "the window must frame low..high";
  if (!(0 <= low && low <= high && high < nums.length)) return `low ${low} and high ${high} are out of order`;
  // The range never loses the smallest number.
  if (!nums.slice(low, high + 1).includes(Math.min(...nums))) return "the smallest number fell out of the range";
  if (s.line === 4 && varOf(s, "middle") !== Math.floor((low + high) / 2)) return "middle is not the middle of low and high";
  if (isLast !== (s.line === 9) || (isLast && low !== high)) return "the trace must end on the return line, when low meets high";
  return sayOk(input, s, prev);
}

export const rotatedSortedArray: Pattern = {
  id: "rotated-sorted-array",
  title: "Rotated sorted array",
  blurb: "A sorted array cut and swapped around: compare the middle with the right end to find the break.",
  problem: "Find the smallest number in a sorted array that has been rotated.",
  section: "Binary search",
  tier: "paid",
  pseudocode,
  fields: [{ name: "nums", label: "Rotated sorted numbers", kind: "ints", min: -99, max: 99, minLen: 1, maxLen: 10 }],
  example: { nums: [4, 5, 6, 1, 2, 3] },
  validate(input) {
    const nums = input.nums as number[];
    const n = nums.length;
    // Going round the circle, the numbers may drop only once.
    const drops = nums.filter((v, i) => v >= nums[(i + 1) % n]).length;
    return n > 1 && drops !== 1 ? "The numbers must be a sorted list, without repeats, cut once and swapped around (such as 4 5 6 1 2 3)." : null;
  },
  random(rng) {
    const sorted: number[] = [];
    let v = pick(rng, 1, 5);
    for (let k = pick(rng, 6, 10); k > 0; k--) sorted.push((v += pick(rng, 1, 4)));
    const cut = pick(rng, 0, sorted.length - 1);
    return { nums: [...sorted.slice(cut), ...sorted.slice(0, cut)] };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => `The smallest number is ${a}`,
};
