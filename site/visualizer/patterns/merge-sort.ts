// Merge sort's merge step: two sorted lists become one, front by front (post 25).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf } from "../schema.ts";
import { arr, eq, pick, ptrs, sayOk, sortedCopy, sortedOnly, step, tiles } from "./_lib.ts";

const pseudocode = [
  "function merge(left, right):",
  "    result = empty list",
  "    i = 0",
  "    j = 0",
  "    while neither list has run out:",
  "        if left[i] <= right[j]:",
  "            append left[i] to result",
  "            i = i + 1",
  "        else:",
  "            append right[j] to result",
  "            j = j + 1",
  "    return result + rest of left and right",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const left = input.left as number[];
  const right = input.right as number[];
  const result: (number | "")[] = Array(left.length + right.length).fill("");
  let i = 0, j = 0, count = 0;
  const snap = (line: number, say: string, newest = -1) =>
    step(line, say, [
      arr("left", tiles(left), (k) => (k < i ? "dim" : k === i ? "gold" : "plain"), ptrs(left.length, { i }), { label: "left", hideIndex: true }),
      arr("right", tiles(right), (k) => (k < j ? "dim" : k === j ? "gold" : "plain"), ptrs(right.length, { j }), { label: "right", hideIndex: true }),
      arr("result", tiles(result), (k) => (k === newest ? "gold" : "steel"), [], { label: "result", hideIndex: true }),
    ]);

  yield snap(3, "i and j point at the front of each sorted list. The smaller front goes to result.");
  while (i < left.length && j < right.length) {
    if (left[i] <= right[j]) {
      result[count++] = left[i++];
      yield snap(7, `${left[i - 1]} is not bigger than ${right[j]}: take it from left.`, count - 1);
    } else {
      result[count++] = right[j++];
      yield snap(10, `${right[j - 1]} is smaller than ${left[i]}: take it from right.`, count - 1);
    }
  }
  for (const v of [...left.slice(i), ...right.slice(j)]) result[count++] = v;
  i = left.length;
  j = right.length;
  yield snap(11, "One list has run out. Whatever is left in the other is already sorted: append it.");
  return result as number[];
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const left = input.left as number[];
  const right = input.right as number[];
  const l = arrayOf(s, "left"), r = arrayOf(s, "right"), out = arrayOf(s, "result");
  if (!l || !r || !out || s.views.length !== 3) return "needs the array views left, right and result";
  if (l.cells.some((c, k) => c.v !== left[k]) || r.cells.some((c, k) => c.v !== right[k])) return "left and right must stay as the input";
  const taken = [l, r].map((v) => v.cells.filter((c) => c.state === "dim").length);
  const filled = out.cells.filter((c) => c.v !== "").map((c) => c.v as number);
  if (out.cells.slice(filled.length).some((c) => c.v !== "")) return "result must fill from the left";
  // result is always the smallest numbers of both lists, in order.
  if (!eq(filled, sortedCopy([...left, ...right]).slice(0, filled.length))) return "result is not the smallest numbers so far, in order";
  if (taken[0] + taken[1] !== filled.length) return "every number in result must be crossed off in its list";
  if (isLast !== (s.line === 11) || (isLast && filled.length !== left.length + right.length)) return "the trace must end with every number in result";
  return sayOk(input, s, prev);
}

export const mergeSort: Pattern = {
  id: "merge-sort",
  title: "Merge sort: the merge",
  blurb: "Two sorted lists into one: compare the two fronts and take the smaller, again and again.",
  problem: "Merge two sorted lists into one sorted list.",
  section: "Recursion and sorting",
  tier: "paid",
  post: "merge-sort",
  pseudocode,
  fields: [
    { name: "left", label: "Sorted list left", kind: "ints", min: -20, max: 99, minLen: 1, maxLen: 4 },
    { name: "right", label: "Sorted list right", kind: "ints", min: -20, max: 99, minLen: 1, maxLen: 4 },
  ],
  example: { left: [1, 4, 7], right: [2, 3, 9] },
  validate: (input) => sortedOnly("Left", input.left as number[]) ?? sortedOnly("Right", input.right as number[]),
  random(rng) {
    const make = () => {
      const a: number[] = [];
      let v = pick(rng, 1, 5);
      for (let k = pick(rng, 2, 4); k > 0; k--) a.push((v += pick(rng, 1, 6)));
      return a;
    };
    return { left: make(), right: make() };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => eq(got, expected),
  answerText: (a) => `Merged: ${(a as number[]).join(", ")}`,
};
