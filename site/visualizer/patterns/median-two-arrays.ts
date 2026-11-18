// Median of two sorted arrays: binary search how many values the shorter array
// gives to the left half, then read the median from the four edges (post 34).
// Each array's frame is the part it gives to the left half.
import type { Answer, ArrayView, Input, Pattern, Step } from "../schema.ts";
import { varOf } from "../schema.ts";
import { arr, list, pick, sayNums, sortedOnly, step, tiles } from "./_lib.ts";

const pseudocode = [
  "function edge(nums, k, empty):",
  "    if k < 0 or k >= length(nums):",
  "        return empty",
  "    return nums[k]",
  "function median(a, b):",
  "    if length(a) > length(b):",
  "        return median(b, a)   // a: shorter",
  "    m = length(a)",
  "    n = length(b)",
  "    half = floor((m + n + 1) / 2)",
  "    low = 0",
  "    high = m",
  "    while low < high:",
  "        i = floor((low + high) / 2)",
  "        if b[half - i - 1] > a[i]:",
  "            low = i + 1   // more from a",
  "        else:",
  "            high = i",
  "    j = half - low   // low = the cut in a",
  "    leftA = edge(a, low - 1, -infinity)",
  "    leftB = edge(b, j - 1, -infinity)",
  "    leftMax = max(leftA, leftB)",
  "    if (m + n) mod 2 == 1:",
  "        return leftMax",
  "    rightA = edge(a, low, infinity)",
  "    rightB = edge(b, j, infinity)",
  "    rightMin = min(rightA, rightB)",
  "    return (leftMax + rightMin) / 2",
];

const show = (x: number) => (x === Infinity ? "infinity" : x === -Infinity ? "-infinity" : String(x));

function* run(input: Input): Generator<Step, Answer, void> {
  const swapped = (input.a as number[]).length > (input.b as number[]).length;
  const a = (swapped ? input.b : input.a) as number[];
  const b = (swapped ? input.a : input.b) as number[];
  const m = a.length, n = b.length;
  const half = Math.floor((m + n + 1) / 2);
  const ta = tiles(a), tb = tiles(b);
  let low = 0, high = m;
  let i: number | "" = "", j: number | "" = "";
  let cutA = 0; // values a gives to the left half in the picture
  let goldA: number[] = [], goldB: number[] = [], steelA: number[] = [], steelB: number[] = [];
  const snap = (line: number, say: string) => {
    const st = (gold: number[], steel: number[]) => (k: number) => (gold.includes(k) ? "gold" : steel.includes(k) ? "steel" : "plain");
    const ptrA = i === "" ? [] : [{ id: "i", label: "i", at: i }];
    return step(line, say, [
      arr("a", ta, st(goldA, steelA), ptrA, { label: "a (the shorter)", window: { lo: 0, hi: cutA - 1 } }),
      arr("b", tb, st(goldB, steelB), [], { label: "b", window: { lo: 0, hi: half - cutA - 1 } }),
    ], { half, low, high, j });
  };

  yield snap(swapped ? 6 : 9, `${swapped ? "The first row is longer, so the two swap. " : ""}The left half holds half = ${half} of the ${m + n} values.`);
  while (low < high) {
    i = Math.floor((low + high) / 2);
    cutA = i;
    goldA = [i];
    goldB = [half - i - 1];
    yield snap(13, `Try i = ${i}: a gives ${i} to the left half, b gives ${half - i}.`);
    const bv = b[half - i - 1], av = a[i];
    if (bv > av) {
      low = i + 1;
      yield snap(15, `b's ${bv} is more than a's ${av}: a must give more. low = ${low}.`);
    } else {
      high = i;
      yield snap(17, `b's ${bv} is not more than a's ${av}: this cut or one further left. high = ${high}.`);
    }
  }
  i = "";
  j = half - low;
  cutA = low;
  goldA = low > 0 ? [low - 1] : [];
  goldB = j > 0 ? [j - 1] : [];
  const leftA = low > 0 ? a[low - 1] : -Infinity, leftB = j > 0 ? b[j - 1] : -Infinity;
  const leftMax = Math.max(leftA, leftB);
  yield snap(18, `The cut is found: a gives low = ${low}, b gives j = ${j}.`);
  yield snap(21, `The left half ends with max(${show(leftA)}, ${show(leftB)}) = ${leftMax}.`);
  if ((m + n) % 2 === 1) {
    yield snap(23, `${m + n} values, an odd count: the median is leftMax, ${leftMax}.`);
    return leftMax;
  }
  steelA = low < m ? [low] : [];
  steelB = j < n ? [j] : [];
  const rightA = low < m ? a[low] : Infinity, rightB = j < n ? b[j] : Infinity;
  const rightMin = Math.min(rightA, rightB);
  yield snap(26, `The right half starts with min(${show(rightA)}, ${show(rightB)}) = ${rightMin}.`);
  const med = (leftMax + rightMin) / 2;
  yield snap(27, `${m + n} values, an even count: the median is (${leftMax} + ${rightMin}) / 2 = ${med}.`);
  return med;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const ia = input.a as number[], ib = input.b as number[];
  const [a, b] = ia.length > ib.length ? [ib, ia] : [ia, ib];
  const half = Math.floor((a.length + b.length + 1) / 2);
  const [va, vb] = s.views as ArrayView[];
  if (s.views.length !== 2 || va.id !== "a" || vb.id !== "b") return "needs the array views a and b";
  if (va.cells.some((c, k) => c.v !== a[k]) || vb.cells.some((c, k) => c.v !== b[k]) || va.cells.length !== a.length) return "a must be the shorter row, b the other";
  const low = varOf(s, "low") as number, high = varOf(s, "high") as number;
  const i: number | "" = va.pointers.length ? va.pointers[0].at : "";
  const j = varOf(s, "j");
  if (varOf(s, "half") !== half) return "half is floor((m + n + 1) / 2)";
  // The two frames together always hold exactly half of the values.
  const ca = va.window ? va.window.hi + 1 : 0, cb = vb.window ? vb.window.hi + 1 : 0;
  if (va.window?.lo !== 0 || vb.window?.lo !== 0 || ca + cb !== half) return `the frames hold ${ca} + ${cb} values, not ${half}`;
  if (!(0 <= low && low <= high && high <= a.length)) return `low ${low} and high ${high} must stay inside 0..${a.length}`;
  // The right cut is always in low..high: a cut c works when b's last left value is not more than a[c].
  const works = (c: number) => (c === a.length || half - c - 1 < 0 || b[half - c - 1] <= a[c]) && (c === 0 || half - c >= b.length || a[c - 1] <= b[half - c]);
  let any = false;
  for (let c = low; c <= high; c++) if (works(c)) any = true;
  if (!any) return `no cut from ${low} to ${high} splits the values correctly`;
  if (i !== "") {
    if (i !== Math.floor((low + high) / 2) && s.line === 13) return "i must be the middle of low and high";
    if (ca !== i) return "a's frame shows the i values a gives";
  }
  if (j !== "" && (j !== half - low || ca !== low)) return "after the search, a gives low values and b gives j";
  const gold = (v: ArrayView) => v.cells.flatMap((c, k) => (c.state === "gold" ? [k] : []));
  if (s.line === 13 && (gold(va).join() !== String(i) || gold(vb).join() !== String(half - (i as number) - 1))) return "the two compared values are lit";
  if (isLast !== (s.line === 23 || s.line === 27)) return "the trace must end on a return line";
  const all = [...a, ...b].sort((x, y) => x - y);
  const med = all.length % 2 ? all[(all.length - 1) / 2] : (all[all.length / 2 - 1] + all[all.length / 2]) / 2;
  return sayNums(input, s, prev, [half - (typeof i === "number" ? i : 0), a.length + b.length, med]);
}

export const medianTwoArrays: Pattern = {
  id: "median-two-arrays",
  title: "Median of two sorted arrays",
  blurb: "Binary search the cut in the shorter array; the median sits at the four edges.",
  problem: "Find the median of all the values of two sorted arrays, without merging them.",
  section: "Binary search",
  tier: "paid",
  pseudocode,
  fields: [
    { name: "a", label: "Sorted a", kind: "ints", min: -99, max: 99, minLen: 1, maxLen: 6 },
    { name: "b", label: "Sorted b", kind: "ints", min: -99, max: 99, minLen: 1, maxLen: 6 },
  ],
  example: { a: [1, 4, 7], b: [2, 3, 6, 9] },
  validate: (input) => sortedOnly("a", input.a as number[]) ?? sortedOnly("b", input.b as number[]),
  random(rng) {
    const srt = (x: number[]) => x.sort((p, q) => p - q);
    return { a: srt(list(rng, pick(rng, 1, 4), 0, 30)), b: srt(list(rng, pick(rng, 2, 6), 0, 30)) };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => Math.abs((got as number) - (expected as number)) < 1e-9,
  answerText: (a) => `Median: ${a}`,
};
