// Quick sort: put one pivot in its final place, then sort each side the same way (post 26).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf, varOf } from "../schema.ts";
import { arr, ascending, eq, list, pick, ptrs, sayOk, sortedCopy, step, swap, tiles, vals } from "./_lib.ts";

const pseudocode = [
  "function partition(nums, low, high):",
  "    pivot = nums[high]",
  "    wall = low   // next small slot",
  "    for j from low to high - 1:",
  "        if nums[j] < pivot:",
  "            swap nums[wall], nums[j]",
  "            wall = wall + 1",
  "    swap nums[wall], nums[high]   // home",
  "    return wall",
  "",
  "// use 1: sort the whole row",
  "function quickSort(nums, low, high):",
  "    if low < high:",
  "        spot = partition(nums, low, high)",
  "        quickSort(nums, low, spot - 1)",
  "        quickSort(nums, spot + 1, high)",
  "",
  "// use 2: only the k-th smallest",
  "function quickSelect(nums, k):",
  "    low = 0",
  "    high = length(nums) - 1",
  "    while true:",
  "        spot = partition(nums, low, high)",
  "        if spot == k - 1:",
  "            return nums[spot]",
  "        if spot < k - 1:",
  "            low = spot + 1",
  "        else:",
  "            high = spot - 1",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const t = tiles(input.nums as number[]);
  const n = t.length;
  const home = new Set<string>(); // ids of the numbers in their final place
  let hot = ""; // id of the pivot being placed
  const snap = (line: number, say: string, low: number, high: number, wall = -1, j = -1, pivot: number | "" = "") =>
    step(
      line,
      say,
      [arr("nums", t, (k) => (home.has(t[k].id) ? "steel" : t[k].id === hot || k === j ? "gold" : k < low || k > high ? "dim" : "plain"), ptrs(n, { wall, j }), { window: { lo: low, hi: high } })],
      { low, high, pivot },
    );

  function* sort(low: number, high: number): Generator<Step, void, void> {
    if (low > high) return;
    if (low === high) {
      home.add(t[low].id); // one number alone is already in place
      return;
    }
    yield snap(13, `Sort index ${low} to ${high}: partition it around its last number.`, low, high);
    const pivot = t[high].v as number;
    hot = t[high].id;
    let wall = low;
    yield snap(2, `The pivot is ${pivot}. wall marks where the next smaller number goes.`, low, high, wall, -1, pivot);
    for (let j = low; j < high; j++) {
      if ((t[j].v as number) < pivot) {
        swap(t, wall, j);
        wall++;
        yield snap(6, `${t[wall - 1].v} is smaller than ${pivot}: it goes to the wall, and the wall moves right.`, low, high, wall, j, pivot);
      } else {
        yield snap(4, `${t[j].v} is not smaller than ${pivot}: leave it where it is.`, low, high, wall, j, pivot);
      }
    }
    swap(t, wall, high);
    home.add(t[wall].id);
    hot = "";
    yield snap(7, `Swap the pivot ${pivot} to the wall. It is home at index ${wall}: smaller on its left, the rest on its right.`, low, high, wall, -1, pivot);
    yield* sort(low, wall - 1);
    yield* sort(wall + 1, high);
  }

  yield* sort(0, n - 1);
  yield snap(12, "Every part is down to one number or none: sorted.", 0, n - 1);
  return t.map((x) => x.v as number);
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const a = arrayOf(s, "nums");
  if (!a?.window || s.views.length !== 1) return "needs exactly the array view nums, with a window";
  const now = vals(s, "nums");
  const final = sortedCopy(nums);
  if (!eq(sortedCopy(now), final)) return "the cells are not the input's numbers";
  for (const [k, c] of a.cells.entries()) if (c.state === "steel" && c.v !== final[k]) return `cell ${k} is marked home but ${c.v} does not belong there`;
  const { lo, hi } = a.window;
  const at = (id: string) => a.pointers.find((p) => p.id === id)?.at;
  const wall = at("wall");
  const pivot = varOf(s, "pivot");
  if (wall !== undefined && typeof pivot === "number" && s.line !== 7) {
    // Left of the wall: smaller than the pivot. From the wall to j: not smaller.
    const j = at("j") ?? wall - 1;
    if (now.slice(lo, wall).some((v) => v >= pivot)) return "a number left of the wall is not smaller than the pivot";
    if (now.slice(wall, j + 1).some((v) => v < pivot)) return "a number between the wall and j is smaller than the pivot";
    if (now[hi] !== pivot) return "the pivot must wait at the right end of the range";
  }
  if (s.line === 7 && (wall === undefined || now[wall] !== pivot || a.cells[wall].state !== "steel")) return "after the last swap the pivot sits at the wall, home";
  if (isLast !== (s.line === 12)) return "the trace must end when every part is sorted";
  if (isLast && (!ascending(now) || a.cells.some((c) => c.state !== "steel"))) return "the trace ends before the row is sorted";
  return sayOk(input, s, prev);
}

export const quickSort: Pattern = {
  id: "quick-sort",
  title: "Quick sort",
  blurb: "Pick a pivot, move the smaller numbers to its left, and it lands in its final place.",
  problem: "Sort the numbers from small to large.",
  section: "Recursion and sorting",
  tier: "paid",
  post: "quick-sort",
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
