// Minimise the largest gap after adding k pumps: binary search the gap d, and
// count the pumps each guess needs (post 33). The guesses are real numbers, shown
// to 6 decimals; the loop runs until high and low are within 0.000001.
import type { Answer, ArrayView, Input, Pattern, Step } from "../schema.ts";
import { varOf } from "../schema.ts";
import { pick, sayNums, step, tiles, arr } from "./_lib.ts";

const pseudocode = [
  "function pumpsNeeded(stations, d):",
  "    count = 0",
  "    for i from 1 to length(stations) - 1:",
  "        gap = stations[i] - stations[i - 1]",
  "        count = count + ceil(gap / d) - 1",
  "    return count",
  "function minMaxGap(stations, k):",
  "    n = length(stations)",
  "    low = 0",
  "    high = stations[n - 1] - stations[0]",
  "    while high - low > 0.000001:",
  "        d = (low + high) / 2",
  "        if pumpsNeeded(stations, d) <= k:",
  "            high = d   // fits: go lower",
  "        else:",
  "            low = d    // too many: go higher",
  "    return high",
];

/** A real number as the narration says it: at most 6 decimals. */
const r6 = (x: number) => Number(x.toFixed(6));
/** The same in a value box: always 6 decimals and the same width, so the boxes never re-wrap. */
const box6 = (x: number) => x.toFixed(6).padStart(9);
const gapsOf = (st: number[]) => st.slice(1).map((v, i) => v - st[i]);

function* run(input: Input): Generator<Step, Answer, void> {
  const st = input.stations as number[];
  const k = input.k as number;
  const gaps = gapsOf(st);
  const gt = tiles(gaps);
  let low = 0, high = st[st.length - 1] - st[0];
  let d: number | "" = "", needed: number | "" = "";
  let pumps: (number | "")[] = gaps.map(() => "");
  const snap = (line: number, say: string) =>
    step(line, say, [
      arr("gaps", gt, (i) => (pumps[i] === "" ? "plain" : (pumps[i] as number) > 0 ? "gold" : "steel"), [], { label: "Gaps between stations" }),
      arr("pumps", tiles(pumps), () => "plain", [], { label: "Pumps each gap needs at d", hideIndex: true }),
    ], { k: String(k).padStart(2), low: box6(low), high: box6(high), d: d === "" ? "" : box6(d), needed: needed === "" ? "" : String(needed).padStart(2) });

  yield snap(9, `The answer lies between low = 0 and high = ${high}, the whole road with no new pumps.`);
  while (high - low > 0.000001) {
    d = (low + high) / 2;
    pumps = gaps.map((g) => Math.ceil(g / (d as number)) - 1);
    needed = pumps.reduce((a: number, b) => a + (b as number), 0);
    yield snap(11, `Try d = ${r6(d)}: the gaps need ${pumps.join(" + ")} = ${needed} pump${needed === 1 ? "" : "s"}.`);
    if (needed <= k) {
      high = d;
      yield snap(13, `${needed} ≤ k = ${k}: d fits, so try lower. high = ${r6(high)}.`);
    } else {
      low = d;
      yield snap(15, `${needed} > k = ${k}: too many pumps, so try higher. low = ${r6(low)}.`);
    }
  }
  yield snap(16, `high and low are within 0.000001: return high, ${r6(high)}.`);
  return high;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const st = input.stations as number[];
  const k = input.k as number;
  const gaps = gapsOf(st);
  const [g, p] = s.views as ArrayView[];
  if (s.views.length !== 2 || g?.id !== "gaps" || p?.id !== "pumps") return "needs the array views gaps and pumps";
  if (g.cells.some((c, i) => c.v !== gaps[i] || c.id !== `c${i}`)) return "gaps must be the distances between neighbouring stations";
  const num = (name: string) => {
    const v = varOf(s, name);
    return v === "" || v === undefined ? "" : Number(v);
  };
  const low = num("low") as number, high = num("high") as number;
  const d = num("d"), needed = num("needed");
  if (!(low >= 0 && low <= high)) return `low ${low} must stay below high ${high}`;
  if (d === "") {
    if (p.cells.some((c) => c.v !== "")) return "no pumps are counted before the first guess";
  } else {
    if (typeof d !== "number" || !(d > low - 1e-6 && d < high + 1e-6)) return "d must lie between low and high";
    // d is shown to 6 decimals: a count is right if it is right for some d within that rounding.
    for (const [i, c] of p.cells.entries()) {
      const a = Math.ceil(gaps[i] / (d + 5e-7)) - 1, b = Math.ceil(gaps[i] / Math.max(d - 5e-7, 1e-9)) - 1;
      if (typeof c.v !== "number" || c.v < a || c.v > b) return `gap ${gaps[i]} needs ${a} pumps at d = ${d}, the step shows ${c.v}`;
    }
    const sum = p.cells.reduce((t, c) => t + (c.v as number), 0);
    if (needed !== sum) return `needed is ${needed}, the gaps add up to ${sum}`;
  }
  if (s.line === 13 && (prev === null || (needed as number) > k || Math.abs(high - Number(varOf(prev, "d"))) > 1e-9)) return "high = d only when d fits";
  if (s.line === 15 && (prev === null || (needed as number) <= k || Math.abs(low - Number(varOf(prev, "d"))) > 1e-9)) return "low = d only when d needs too many pumps";
  // Each guess halves the range.
  if (prev && (s.line === 13 || s.line === 15)) {
    const before = Number(varOf(prev, "high")) - Number(varOf(prev, "low"));
    if (Math.abs((high - low) * 2 - before) > 4e-6) return "each guess must halve the range";
  }
  if (isLast !== (s.line === 16) || (s.line === 16 && high - low > 0.0000021)) return "the trace ends on 'return high' once the range is under 0.000001";
  const shown = prev ? ["low", "high", "d"].map((n) => Number(varOf(prev, n))) : [];
  return sayNums(input, s, prev, [0.000001, k, low, high, typeof d === "number" ? d : 0, typeof needed === "number" ? needed : 0, ...shown]);
}

export const gasStations: Pattern = {
  id: "gas-stations",
  title: "Minimise the largest gap",
  blurb: "Binary search the answer itself: guess the largest gap d, count the pumps it needs.",
  problem: "Add k pumps to the road so the largest gap between neighbours is as small as it can be.",
  section: "Binary search",
  tier: "paid",
  pseudocode,
  fields: [
    { name: "stations", label: "Stations, left to right", kind: "ints", min: 0, max: 99, minLen: 2, maxLen: 6 },
    { name: "k", label: "New pumps k", kind: "int", min: 0, max: 9 },
  ],
  example: { stations: [1, 3, 12, 16], k: 3 },
  validate(input) {
    const st = input.stations as number[];
    for (let i = 1; i < st.length; i++) if (st[i] <= st[i - 1]) return `Stations must go up from left to right: ${st[i]} comes after ${st[i - 1]}.`;
    return null;
  },
  random(rng) {
    const st = [pick(rng, 0, 9)];
    for (let i = pick(rng, 2, 5); i > 0; i--) st.push(st[st.length - 1] + pick(rng, 1, 15));
    return { stations: st, k: pick(rng, 1, 6) };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => Math.abs((got as number) - (expected as number)) < 1e-5,
  answerText: (a) => `Smallest largest gap: ${(a as number).toFixed(2)}`,
};
