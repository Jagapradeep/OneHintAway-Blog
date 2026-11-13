// Next permutation: the next larger order of the same numbers (LeetCode 31, post 17).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf, varOf } from "../schema.ts";
import { arr, eq, list, pick, ptrs, sayOk, sortedCopy, step, swap, tiles, vals } from "./_lib.ts";

const pseudocode = [
  "function nextPermutation(nums):",
  "    n = length(nums)",
  "    i = n - 2",
  "    while i >= 0 and nums[i] >= nums[i + 1]:",
  "        i = i - 1                // walk left",
  "    if i >= 0:                   // pivot found",
  "        j = n - 1",
  "        while nums[j] <= nums[i]:",
  "            j = j - 1",
  "        swap nums[i], nums[j]",
  "    reverse nums from i + 1 to n - 1",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const t = tiles(input.nums as number[]);
  const n = t.length;
  let i = n - 2, j = -1;
  // Cells from `tail` on are the reversed tail.
  const snap = (line: number, say: string, gold: number[] = [], tail = n) =>
    step(line, say, [arr("nums", t, (k) => (gold.includes(k) ? "gold" : k >= tail ? "steel" : "plain"), ptrs(n, { i, j }))], { i, j: j < 0 ? "" : j });

  yield snap(2, i >= 0 ? "Start at the second-to-last number. Look for one that is smaller than its right neighbour." : "A single number has only one order.", [i, i + 1]);
  while (i >= 0 && t[i].v >= t[i + 1].v) {
    i--;
    yield snap(4, `${t[i + 1].v} is not smaller than ${t[i + 2].v}: walk left.`, i >= 0 ? [i, i + 1] : []);
  }
  if (i >= 0) {
    yield snap(5, `${t[i].v} is smaller than ${t[i + 1].v}: this is the pivot, the number to raise.`, [i]);
    j = n - 1;
    yield snap(6, `From the right end, look for the first number bigger than ${t[i].v}.`, [i, j]);
    while (t[j].v <= t[i].v) {
      j--;
      yield snap(8, `${t[j + 1].v} is not bigger than ${t[i].v}: step left.`, [i, j]);
    }
    swap(t, i, j);
    yield snap(9, `${t[i].v} is the smallest number on the right that is bigger than ${t[j].v}: swap them.`, [i, j]);
  }
  for (let a = i + 1, b = n - 1; a < b; a++, b--) swap(t, a, b);
  yield snap(10, i >= 0 ? `Reverse everything after index ${i}, so the tail is as small as it can be.` : "No pivot: this was the largest order. Reverse it all to get the smallest.", [], i + 1);
  return t.map((x) => x.v as number);
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const a = arrayOf(s, "nums");
  if (!a || s.views.length !== 1) return "needs exactly the array view nums";
  const now = vals(s, "nums");
  if (!eq(sortedCopy(now), sortedCopy(nums))) return "the cells are not the input's numbers";
  const i = varOf(s, "i") as number;
  if (s.line < 9 && !eq(now, nums)) return "nothing may move before the swap";
  // Everything right of i never climbs: that is why i is the right place to change.
  if (s.line >= 4 && s.line <= 9 && now.slice(i + 1).some((v, k, tail) => k > 0 && tail[k - 1] < v)) return "the numbers right of i must not climb";
  if (isLast !== (s.line === 10)) return "the trace must end on the reverse";
  if (isLast) {
    if (i >= 0 && !(nums[i] < now[i] && eq(now.slice(0, i), nums.slice(0, i)))) return "the pivot must be raised and everything left of it kept";
    if (now.slice(i + 1).some((v, k, tail) => k > 0 && tail[k - 1] > v)) return "the tail must end up climbing";
  }
  return sayOk(input, s, prev);
}

export const nextPermutation: Pattern = {
  id: "next-permutation",
  title: "Next permutation",
  blurb: "The next larger order of the same numbers: find the pivot, raise it a little, shrink the tail.",
  problem: "Rearrange the numbers into the next larger order.",
  section: "Arrays and hashing",
  tier: "paid",
  post: "next-permutation",
  pseudocode,
  fields: [{ name: "nums", label: "Numbers", kind: "ints", min: 0, max: 99, minLen: 1, maxLen: 7 }],
  example: { nums: [1, 3, 5, 4, 2] },
  validate: () => null,
  random: (rng) => ({ nums: list(rng, pick(rng, 4, 6), 1, 9) }),
  run,
  check,
  sameAnswer: (_i, got, expected) => eq(got, expected),
  answerText: (a) => `Next order: ${(a as number[]).join(", ")}`,
};
