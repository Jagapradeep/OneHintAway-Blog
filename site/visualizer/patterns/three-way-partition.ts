// Three-way partition: sort 0s, 1s and 2s in one pass (LeetCode 75, post 13).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf, varOf } from "../schema.ts";
import { arr, ascending, eq, list, pick, ptrs, sayOk, sortedCopy, step, swap, tiles, vals } from "./_lib.ts";

const pseudocode = [
  "low = 0                   // next 0 goes here",
  "mid = 0                   // number to check",
  "high = length(nums) - 1   // next 2 goes here",
  "while mid <= high:",
  "    if nums[mid] == 0:",
  "        swap nums[low], nums[mid]",
  "        low = low + 1",
  "        mid = mid + 1",
  "    else if nums[mid] == 1:",
  "        mid = mid + 1",
  "    else:",
  "        swap nums[mid], nums[high]",
  "        high = high - 1   // mid stays",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const t = tiles(input.nums as number[]);
  const n = t.length;
  let low = 0, mid = 0, high = n - 1;
  const snap = (line: number, say: string) =>
    step(line, say, [arr("nums", t, (k) => (k === mid && mid <= high ? "gold" : k < low || k > high ? "steel" : "plain"), ptrs(n, { low, mid, high }))], { low, mid, high });

  yield snap(2, "low and mid start on the left, high on the right. mid checks one number at a time.");
  while (mid <= high) {
    const v = t[mid].v;
    if (v === 0) {
      swap(t, low, mid);
      low++;
      mid++;
      yield snap(7, "A 0: swap it to the low spot. low and mid both move right.");
    } else if (v === 1) {
      mid++;
      yield snap(9, "A 1 is already in the middle zone. mid moves right.");
    } else {
      swap(t, mid, high);
      high--;
      yield snap(12, "A 2: swap it to the high spot. high moves left; mid stays to check the new number.");
    }
  }
  yield snap(3, "mid has passed high, so every number is checked: 0s, then 1s, then 2s.");
  return t.map((x) => x.v as number);
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const a = arrayOf(s, "nums");
  if (!a || s.views.length !== 1) return "needs exactly the array view nums";
  const now = vals(s, "nums");
  if (!eq(sortedCopy(now), sortedCopy(nums))) return "the cells are not the input's numbers";
  const low = varOf(s, "low") as number, mid = varOf(s, "mid") as number, high = varOf(s, "high") as number;
  if (!(0 <= low && low <= mid && mid <= high + 1 && high < nums.length)) return `low ${low}, mid ${mid}, high ${high} are out of order`;
  // The three zones: 0s before low, 1s from low up to mid, 2s after high.
  if (now.slice(0, low).some((v) => v !== 0)) return "a number before low is not 0";
  if (now.slice(low, mid).some((v) => v !== 1)) return "a number between low and mid is not 1";
  if (now.slice(high + 1).some((v) => v !== 2)) return "a number after high is not 2";
  if (isLast !== (s.line === 3)) return "the trace must end when mid has passed high";
  if (isLast && (mid <= high || !ascending(now))) return "the trace ends before every number is checked";
  return sayOk(input, s, prev, [0, 1, 2]);
}

export const threeWayPartition: Pattern = {
  id: "three-way-partition",
  title: "Three-way partition",
  blurb: "Only 0s, 1s and 2s: three pointers sort them in a single pass.",
  problem: "Sort an array of 0s, 1s and 2s in one pass.",
  section: "Arrays and hashing",
  tier: "paid",
  post: "three-way-partition",
  pseudocode,
  fields: [{ name: "nums", label: "Numbers (only 0, 1, 2)", kind: "ints", min: 0, max: 2, minLen: 1, maxLen: 10 }],
  example: { nums: [2, 0, 2, 1, 1, 0] },
  validate: () => null,
  random: (rng) => ({ nums: list(rng, pick(rng, 6, 9), 0, 2) }),
  run,
  check,
  sameAnswer: (_i, got, expected) => eq(got, expected),
  answerText: (a) => `Sorted: ${(a as number[]).join(", ")}`,
};
