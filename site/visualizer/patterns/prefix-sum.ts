// Prefix sum: build the running totals once, then any range sum is one subtraction (LeetCode 303, post 10).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf, varOf } from "../schema.ts";
import { arr, list, pick, sayOk, step, sum, tiles } from "./_lib.ts";

const pseudocode = [
  "function buildPrefix(nums):",
  "    n = length(nums)",
  "    prefix = array of n + 1 zeros",
  "    for i from 0 to n - 1:",
  "        prefix[i + 1] = prefix[i] + nums[i]",
  "    return prefix",
  "",
  "function rangeSum(prefix, left, right):",
  "    return prefix[right + 1] - prefix[left]",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const left = input.left as number;
  const right = input.right as number;
  const n = nums.length;
  const prefix: number[] = Array(n + 1).fill(0);
  let filled = 0;
  let total: number | "" = "";
  const snap = (line: number, say: string, at = -1, gold = -1, steel = -1, query = false) =>
    step(
      line,
      say,
      [
        arr("nums", tiles(nums), (i) => (i === at ? "gold" : query && (i < left || i > right) ? "dim" : "plain"), [], { window: query ? { lo: left, hi: right } : { lo: 0, hi: -1 }, label: "nums" }),
        arr("prefix", tiles(prefix), (i) => (i === gold ? "gold" : i === steel ? "steel" : i > filled ? "dim" : "plain"), [], { label: "prefix · sums before each index" }),
      ],
      { left, right, sum: total },
    );

  yield snap(2, `prefix gets ${n + 1} slots. prefix[0] stays 0: nothing comes before index 0.`);
  for (let i = 0; i < n; i++) {
    prefix[i + 1] = prefix[i] + nums[i];
    filled = i + 1;
    yield snap(4, `prefix[${i + 1}] = ${prefix[i]} + ${nums[i]} = ${prefix[i + 1]}.`, i, i + 1, i);
  }
  yield snap(5, "prefix is built once. From now on, any range sum is one subtraction.");
  total = prefix[right + 1] - prefix[left];
  yield snap(8, `Index ${left} to ${right}: prefix[${right + 1}] minus prefix[${left}] is ${prefix[right + 1]} minus ${prefix[left]} = ${total}.`, -1, right + 1, left, true);
  return total;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const left = input.left as number;
  const right = input.right as number;
  const a = arrayOf(s, "nums");
  const p = arrayOf(s, "prefix");
  if (!a?.window || !p || s.views.length !== 2) return "needs the array views nums and prefix";
  if (a.cells.some((c, i) => c.v !== nums[i])) return "nums must stay as the input";
  if (p.cells.length !== nums.length + 1) return "prefix needs one slot more than nums";
  // A slot that is not dimmed is filled in, and must be the true sum of everything before it.
  for (const [i, c] of p.cells.entries()) {
    if (c.state === "dim" ? c.v !== 0 : c.v !== sum(nums.slice(0, i))) return `prefix[${i}] shows ${c.v}`;
    if (i > 0 && c.state !== "dim" && p.cells[i - 1].state === "dim") return "prefix must fill from the left";
  }
  if (isLast !== (s.line === 8)) return "the trace must end on the range sum";
  if (isLast) {
    if (p.cells.some((c) => c.state === "dim")) return "the range sum needs the whole prefix";
    if (varOf(s, "sum") !== sum(nums.slice(left, right + 1))) return `sum is ${varOf(s, "sum")}, the range adds up to ${sum(nums.slice(left, right + 1))}`;
    if (a.window.lo !== left || a.window.hi !== right) return "the window must frame left..right";
  } else if (varOf(s, "sum") !== "") return "sum is set only by the range sum";
  return sayOk(input, s, prev);
}

export const prefixSum: Pattern = {
  id: "prefix-sum",
  title: "Prefix sum",
  blurb: "Add up the array once, and every range sum after that is a single subtraction.",
  problem: "Find the sum of the numbers from index left to index right.",
  section: "Arrays and hashing",
  tier: "paid",
  post: "prefix-sum",
  pseudocode,
  fields: [
    { name: "nums", label: "Numbers", kind: "ints", min: -20, max: 50, minLen: 1, maxLen: 8 },
    { name: "left", label: "Left index", kind: "int", min: 0, max: 7 },
    { name: "right", label: "Right index", kind: "int", min: 0, max: 7 },
  ],
  example: { nums: [3, 1, 4, 1, 5], left: 1, right: 3 },
  validate(input) {
    const n = (input.nums as number[]).length;
    const left = input.left as number;
    const right = input.right as number;
    return left > right ? "Left index can't be after right index." : right >= n ? `Right index can be ${n - 1} at most.` : null;
  },
  random(rng) {
    const nums = list(rng, pick(rng, 4, 7), -5, 15);
    const left = pick(rng, 0, nums.length - 1);
    return { nums, left, right: pick(rng, left, nums.length - 1) };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => `The range adds up to ${a}`,
};
