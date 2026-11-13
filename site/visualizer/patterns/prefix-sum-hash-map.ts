// Prefix sum with a hash map: count the runs that add up to k (LeetCode 560, post 11).
import type { Answer, Input, NodeState, Pattern, Step } from "../schema.ts";
import { arrayOf, mapOf, pointerAt, varOf } from "../schema.ts";
import { arr, eq, list, pick, ptrs, sayOk, step, sum, tiles } from "./_lib.ts";

const pseudocode = [
  "function subarraySum(nums, k):",
  "    seen = empty map  // sum -> times seen",
  "    seen[0] = 1       // the empty start",
  "    sum = 0",
  "    count = 0",
  "    for each x in nums:",
  "        sum = sum + x",
  "        count = count + seen[sum - k]",
  "        seen[sum] = seen[sum] + 1",
  "    return count",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const k = input.k as number;
  const n = nums.length;
  const seen = new Map<number, number>([[0, 1]]);
  let total = 0, count = 0;
  let hot: number | "" = "";
  const snap = (line: number, say: string, i: number) =>
    step(
      line,
      say,
      [
        arr("nums", tiles(nums), (j) => (j === i ? "gold" : j < i ? "dim" : "plain"), ptrs(n, { x: i })),
        { kind: "map", id: "seen", label: "seen · running sum → times seen", entries: [...seen].map(([key, v]) => ({ id: `k${key}`, k: key, v, state: (key === hot ? "gold" : "plain") as NodeState })) },
      ],
      { k, sum: total, count },
    );

  yield snap(4, "seen starts with the sum 0, seen 1 time: the empty start.", -1);
  for (let i = 0; i < n; i++) {
    total += nums[i];
    hot = "";
    yield snap(6, `Add ${nums[i]}: the running sum is ${total}.`, i);
    const hit = seen.get(total - k) ?? 0;
    count += hit;
    hot = hit ? total - k : "";
    yield snap(7, hit ? `${total} minus ${k} is ${total - k}, seen ${hit} time(s): ${hit} more run(s) end here. count = ${count}.` : `${total} minus ${k} is ${total - k}, never seen: no run ends here.`, i);
    seen.set(total, (seen.get(total) ?? 0) + 1);
    hot = total;
    yield snap(8, `Remember the running sum ${total}: seen ${seen.get(total)} time(s).`, i);
  }
  hot = "";
  yield snap(9, `${count} run(s) of numbers add up to ${k}.`, n);
  return count;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const k = input.k as number;
  const a = arrayOf(s, "nums");
  const m = mapOf(s, "seen");
  if (!a || !m || s.views.length !== 2) return "needs the array view nums and the map view seen";
  if (a.cells.some((c, i) => c.v !== nums[i])) return "the cells must stay as the input";
  const x = pointerAt(s, "x");
  if ((x === undefined) !== (s.line === 4 || s.line === 9)) return "the pointer x is on a number exactly while the loop runs";
  const added = s.line === 4 ? 0 : s.line === 9 ? nums.length : x! + 1; // numbers in the running sum
  const stored = s.line === 6 || s.line === 7 ? added - 1 : added; // running sums in seen, after the empty start
  const counted = s.line === 6 ? added - 1 : added; // run ends already counted
  const P = Array.from({ length: nums.length + 1 }, (_, i) => sum(nums.slice(0, i)));
  if (varOf(s, "sum") !== P[added]) return `sum is ${varOf(s, "sum")}, the first ${added} numbers add up to ${P[added]}`;
  const want: Record<string, number> = {};
  for (const p of P.slice(0, stored + 1)) want[p] = (want[p] ?? 0) + 1;
  if (!eq(Object.fromEntries(m.entries.map((e) => [String(e.k), e.v])), want)) return "seen does not hold exactly the running sums so far";
  let runs = 0;
  for (let e = 1; e <= counted; e++) for (let b = 0; b < e; b++) if (P[e] - P[b] === k) runs++;
  if (varOf(s, "count") !== runs) return `count is ${varOf(s, "count")}, ${runs} runs ending so far add up to k`;
  if (isLast !== (s.line === 9)) return "the trace must end on 'return count'";
  return sayOk(input, s, prev, [P[added] - k]);
}

export const prefixSumHashMap: Pattern = {
  id: "prefix-sum-hash-map",
  title: "Prefix sum with a hash map",
  blurb: "Count the runs that add up to k: a run ends here if the right running sum was seen before.",
  problem: "Count the runs of numbers in a row that add up to k.",
  section: "Arrays and hashing",
  tier: "paid",
  post: "prefix-sum-hash-map",
  pseudocode,
  fields: [
    { name: "nums", label: "Numbers", kind: "ints", min: -9, max: 9, minLen: 1, maxLen: 7 },
    { name: "k", label: "Wanted sum k", kind: "int", min: -30, max: 30 },
  ],
  example: { nums: [1, 2, 3, -3, 3], k: 3 },
  validate: () => null,
  random: (rng) => ({ nums: list(rng, pick(rng, 4, 6), -2, 4), k: pick(rng, 2, 5) }),
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => `Runs that add up to k: ${a}`,
};
