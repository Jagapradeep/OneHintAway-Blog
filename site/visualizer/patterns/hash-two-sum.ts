// Hashing: two numbers that add up to the target, in one pass with a map (LeetCode 1, post 05).
import type { Answer, Input, NodeState, Pattern, Step } from "../schema.ts";
import { arrayOf, mapOf, pointerAt, varOf } from "../schema.ts";
import { arr, eq, list, pick, ptrs, sayOk, step, tiles } from "./_lib.ts";

const pseudocode = [
  "function countLetters(word):",
  "    counts = empty map",
  "    for each ch in word:",
  "        if ch in counts:",
  "            counts[ch] = counts[ch] + 1",
  "        else:",
  "            counts[ch] = 1",
  "    return counts",
  "",
  "function twoSum(nums, target):",
  "    seen = empty map          // value -> index",
  "    for i from 0 to length(nums) - 1:",
  "        need = target - nums[i]",
  "        if need in seen:",
  "            return [seen[need], i]",
  "        seen[nums[i]] = i",
  "    return none",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const target = input.target as number;
  const n = nums.length;
  const seen = new Map<number, number>();
  let hot: number | "" = "";
  let need: number | "" = "";
  const snap = (line: number, say: string, i: number, j = -1) =>
    step(
      line,
      say,
      [
        arr("nums", tiles(nums), (k) => (k === i || k === j ? "gold" : k < i ? "dim" : "plain"), ptrs(n, { i })),
        { kind: "map", id: "seen", label: "seen · value → index", entries: [...seen].map(([k, v]) => ({ id: `k${k}`, k, v, state: (k === hot ? "gold" : "plain") as NodeState })) },
      ],
      { target, need },
    );

  yield snap(10, "seen is empty. It will remember each value and the index it was at.", -1);
  for (let i = 0; i < n; i++) {
    need = target - nums[i];
    hot = seen.has(need) ? need : "";
    yield snap(12, `nums[${i}] is ${nums[i]}, so its partner would be ${need}.`, i);
    if (seen.has(need)) {
      const j = seen.get(need)!;
      yield snap(14, `${need} is in seen, at index ${j}. Found the pair.`, i, j);
      return [j, i];
    }
    seen.set(nums[i], i);
    hot = nums[i];
    yield snap(15, `${need} is not in seen. Remember ${nums[i]} at index ${i}.`, i);
  }
  hot = "";
  yield snap(16, `No two numbers add up to ${target}.`, n);
  return null;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const target = input.target as number;
  const a = arrayOf(s, "nums");
  const m = mapOf(s, "seen");
  if (!a || !m || s.views.length !== 2) return "needs the array view nums and the map view seen";
  if (a.cells.some((c, i) => c.v !== nums[i] || c.id !== `c${i}`)) return "the cells must stay as the input";
  const i = pointerAt(s, "i");
  if ((i === undefined) !== (s.line === 10 || s.line === 16)) return "the pointer i is on a number exactly while the loop runs";
  // seen holds every value before i (and nums[i] too, once it is stored), with its latest index.
  const stored = s.line === 10 ? 0 : s.line === 16 ? nums.length : i! + (s.line === 15 ? 1 : 0);
  const want: Record<string, number> = {};
  nums.slice(0, stored).forEach((v, k) => (want[v] = k));
  if (!eq(Object.fromEntries(m.entries.map((e) => [String(e.k), e.v])), want)) return "seen does not hold exactly the values passed so far";
  if (i !== undefined && varOf(s, "need") !== target - nums[i]) return `need must be ${target} minus nums[${i}]`;
  if (s.line === 14 && (want[target - nums[i!]] === undefined || !isLast)) return "'found' needs the partner in seen, and ends the trace";
  if (isLast !== (s.line === 14 || s.line === 16)) return "the trace must end on a return line";
  return sayOk(input, s, prev);
}

export const hashTwoSum: Pattern = {
  id: "hash-two-sum",
  title: "Hashing: two sum",
  blurb: "Remember what you have seen in a map, and the partner of each number is one lookup away.",
  problem: "Find the two numbers that add up to the target, in one pass.",
  section: "Foundations",
  tier: "paid",
  post: "hashing",
  pseudocode,
  fields: [
    { name: "nums", label: "Numbers", kind: "ints", min: -50, max: 50, minLen: 2, maxLen: 8 },
    { name: "target", label: "Target", kind: "int", min: -100, max: 100 },
  ],
  example: { nums: [3, 8, 11, 6, 2], target: 8 },
  validate: () => null,
  random(rng) {
    const nums = list(rng, pick(rng, 5, 7), 1, 20);
    const j = pick(rng, 1, nums.length - 1);
    return { nums, target: rng() < 0.85 ? nums[j] + nums[pick(rng, 0, j - 1)] : 99 };
  },
  run,
  check,
  sameAnswer(input, got, expected) {
    if (got === null || expected === null) return got === expected;
    const nums = input.nums as number[];
    const [x, y] = got as number[];
    return Array.isArray(got) && got.length === 2 && x !== y && nums[x] + nums[y] === input.target;
  },
  answerText: (a) => (Array.isArray(a) ? `Indexes ${a[0]} and ${a[1]}` : "No pair adds up to the target"),
};
