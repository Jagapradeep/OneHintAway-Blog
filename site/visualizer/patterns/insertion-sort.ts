// Insertion sort: pick up one card at a time and slide it left into place (post 22).
// The card is drawn moving left one place per shift, which is what the copies add up to.
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf } from "../schema.ts";
import { arr, ascending, eq, list, pick, ptrs, sayOk, sortedCopy, step, swap, tiles, vals } from "./_lib.ts";

const pseudocode = [
  "function insertionSort(nums):",
  "    for i from 1 to length(nums) - 1:",
  "        card = nums[i]   // pick it up",
  "        j = i - 1",
  "        while j >= 0 and nums[j] > card:",
  "            nums[j + 1] = nums[j]",
  "            j = j - 1",
  "        nums[j + 1] = card   // drop it in",
  "    return nums",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const t = tiles(input.nums as number[]);
  const n = t.length;
  // at = where the card is now (-1: no card in hand); done = the last index of the sorted part.
  const snap = (line: number, say: string, i: number, at: number, done: number, card: number | "") =>
    step(line, say, [arr("nums", t, (k) => (k === at ? "gold" : k <= done ? "steel" : "plain"), ptrs(n, { card: at }))], { i, card });

  for (let i = 1; i < n; i++) {
    const card = t[i].v as number;
    let j = i - 1;
    yield snap(2, `Pick up ${card}. Everything to its left is already sorted.`, i, i, i - 1, card);
    while (j >= 0 && (t[j].v as number) > card) {
      swap(t, j, j + 1);
      j--;
      yield snap(6, `${t[j + 2].v} is bigger than ${card}: it shifts one place right.`, i, j + 1, i, card);
    }
    yield snap(7, j >= 0 ? `${t[j].v} is not bigger than ${card}: drop ${card} right here.` : `Nothing to the left is smaller: ${card} goes to the front.`, i, -1, i, card);
  }
  yield snap(8, "Every card has been placed: sorted.", n - 1, -1, n - 1, "");
  return t.map((x) => x.v as number);
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const a = arrayOf(s, "nums");
  if (!a || s.views.length !== 1) return "needs exactly the array view nums";
  const now = vals(s, "nums");
  if (!eq(sortedCopy(now), sortedCopy(nums))) return "the cells are not the input's numbers";
  // The sorted part (steel) is in order, with the card in hand left out; the rest is untouched input.
  if (!ascending(a.cells.filter((c) => c.state === "steel").map((c) => c.v as number))) return "the sorted part is out of order";
  const firstPlain = a.cells.findIndex((c) => c.state === "plain");
  if (firstPlain >= 0 && !eq(now.slice(firstPlain), nums.slice(firstPlain))) return "numbers right of the sorted part must be untouched";
  if (isLast !== (s.line === 8)) return "the trace must end on 'return nums'";
  if (isLast && (!ascending(now) || firstPlain >= 0)) return "the trace ends before the row is sorted";
  return sayOk(input, s, prev);
}

export const insertionSort: Pattern = {
  id: "insertion-sort",
  title: "Insertion sort",
  blurb: "Like sorting a hand of cards: pick up the next one and slide it left until it fits.",
  problem: "Sort the numbers from small to large.",
  section: "Recursion and sorting",
  tier: "paid",
  post: "insertion-sort",
  pseudocode,
  fields: [{ name: "nums", label: "Numbers", kind: "ints", min: -20, max: 99, minLen: 1, maxLen: 7 }],
  example: { nums: [5, 2, 8, 1, 4] },
  validate: () => null,
  random: (rng) => ({ nums: list(rng, pick(rng, 4, 6), 1, 30) }),
  run,
  check,
  sameAnswer: (_i, got, expected) => eq(got, expected),
  answerText: (a) => `Sorted: ${(a as number[]).join(", ")}`,
};
