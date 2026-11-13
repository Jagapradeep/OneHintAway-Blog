// Cyclic sort: send every number to the index with its own value, then spot the gap (LeetCode 268, post 15).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf } from "../schema.ts";
import { arr, eq, pick, ptrs, sayOk, sortedCopy, step, swap, tiles, vals } from "./_lib.ts";

const pseudocode = [
  "function missingNumber(nums):",
  "    n = length(nums)",
  "    i = 0",
  "    while i < n:",
  "        seat = nums[i]",
  "        if seat < n and nums[seat] != seat:",
  "            swap nums[i], nums[seat]",
  "        else:",
  "            i = i + 1          // home, or no seat",
  "    for i from 0 to n - 1:",
  "        if nums[i] != i:       // wrong number",
  "            return i",
  "    return n",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const t = tiles(input.nums as number[]);
  const n = t.length;
  let i = 0;
  // A number sitting at the index with its own value is home.
  const snap = (line: number, say: string, seat: number | "" = "", focus = -1) =>
    step(line, say, [arr("nums", t, (k) => (k === focus ? "gold" : t[k].v === k ? "steel" : "plain"), ptrs(n, { i }))], { n, seat });

  yield snap(2, "Every number belongs at the index with its own value. Start at index 0.");
  while (i < n) {
    const seat = t[i].v as number;
    if (seat < n && t[seat].v !== seat) {
      swap(t, i, seat);
      yield snap(6, `${seat} belongs at index ${seat}: swap it home. Index ${i} now holds a new number to check.`, seat, seat);
    } else {
      i++;
      yield snap(8, seat < n ? `${seat} is already home. Move on.` : `${seat} has no seat: the last index is ${n - 1}. Move on.`, seat, i - 1);
    }
  }
  for (i = 0; i < n; i++) {
    if (t[i].v !== i) {
      yield snap(11, `Index ${i} holds ${t[i].v}, not ${i}: the missing number is ${i}.`, "", i);
      return i;
    }
  }
  yield snap(12, `Every index holds its own number, so the missing one is ${n}.`);
  return n;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const a = arrayOf(s, "nums");
  if (!a || s.views.length !== 1) return "needs exactly the array view nums";
  const now = vals(s, "nums");
  if (!eq(sortedCopy(now), sortedCopy(nums))) return "the cells are not the input's numbers";
  for (const [k, c] of a.cells.entries()) {
    if (c.state === "steel" && c.v !== k) return `cell ${k} is marked home but holds ${c.v}`;
    if (c.state === "plain" && c.v === k) return `cell ${k} is home but not marked`;
  }
  if (isLast !== (s.line === 11 || s.line === 12)) return "the trace must end on a return line";
  if (isLast) {
    const gap = now.findIndex((v, k) => v !== k);
    // Once every number that has a seat is home, the first index with a stranger is the answer.
    if (now.some((v, k) => v < now.length && now[v] !== v && v !== k)) return "the scan starts before every number is home";
    if (s.line === 12 ? gap !== -1 : a.pointers[0]?.at !== gap) return "the answer must be the first index holding the wrong number";
  }
  return sayOk(input, s, prev);
}

export const cyclicSort: Pattern = {
  id: "cyclic-sort",
  title: "Cyclic sort",
  blurb: "Numbers 0 to n with one missing: swap each number to its own index and the gap shows itself.",
  problem: "The array holds every number from 0 to n except one. Find the missing one.",
  section: "Arrays and hashing",
  tier: "paid",
  post: "cyclic-sort",
  pseudocode,
  fields: [{ name: "nums", label: "Numbers 0 to n, one missing", kind: "ints", min: 0, max: 8, minLen: 1, maxLen: 8 }],
  example: { nums: [4, 0, 3, 1] },
  validate(input) {
    const nums = input.nums as number[];
    if (new Set(nums).size !== nums.length) return "Every number may appear only once.";
    return nums.some((v) => v > nums.length) ? `With ${nums.length} numbers, the largest allowed is ${nums.length}.` : null;
  },
  random(rng) {
    const n = pick(rng, 4, 7);
    const all = Array.from({ length: n + 1 }, (_, k) => k);
    for (let k = n; k > 0; k--) swap(all, k, pick(rng, 0, k));
    return { nums: all.slice(0, n) };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => `The missing number is ${a}`,
};
