// Binary search on answers: the slowest eating speed that still finishes in time (LeetCode 875, post 32).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf, varOf } from "../schema.ts";
import { arr, list, pick, ptrs, sayOk, step, sum, tiles } from "./_lib.ts";

const pseudocode = [
  "function minSpeed(piles, hours):",
  "    low = 1",
  "    high = max(piles)",
  "    while low < high:",
  "        speed = floor((low + high) / 2)",
  "        if hoursAt(piles, speed) <= hours:",
  "            high = speed   // fast enough",
  "        else:",
  "            low = speed + 1   // too slow",
  "    return low",
];

const perPile = (piles: number[], speed: number) => piles.map((p) => Math.ceil(p / speed));

function* run(input: Input): Generator<Step, Answer, void> {
  const piles = input.piles as number[];
  const hours = input.hours as number;
  const top = Math.max(...piles);
  const speeds = Array.from({ length: top }, (_, k) => k + 1);
  let low = 1, high = top;
  let speed: number | "" = "", needs: number | "" = "";
  const snap = (line: number, say: string, focus = false) =>
    step(
      line,
      say,
      [
        arr("piles", tiles(piles), () => "plain", [], { label: "piles of bananas", hideIndex: true }),
        arr("speeds", tiles(speeds), (k) => (focus && k + 1 === speed ? "gold" : k + 1 < low || k + 1 > high ? "dim" : "plain"), ptrs(top, speed === "" ? {} : { speed: speed - 1 }), {
          window: { lo: low - 1, hi: high - 1 },
          label: "speeds that could be the answer",
          hideIndex: true,
        }),
      ],
      { hours, speed, needs },
    );

  yield snap(2, `The answer is a speed from 1 to ${top}, the biggest pile. Find the slowest that fits in ${hours} hours.`);
  while (low < high) {
    speed = Math.floor((low + high) / 2);
    needs = sum(perPile(piles, speed));
    yield snap(4, `Try speed ${speed}: the piles take ${perPile(piles, speed).join(" + ")} = ${needs} hours.`, true);
    if (needs <= hours) {
      high = speed;
      yield snap(6, `${needs} fits in ${hours} hours: ${speed} works, and something slower might too. high = ${high}.`);
    } else {
      low = speed + 1;
      yield snap(8, `${needs} is more than ${hours} hours: ${speed} is too slow. low = ${low}.`);
    }
  }
  yield snap(9, `low and high meet: ${low} is the slowest speed that finishes in time.`);
  return low;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const piles = input.piles as number[];
  const hours = input.hours as number;
  const p = arrayOf(s, "piles");
  const sp = arrayOf(s, "speeds");
  if (!p || !sp?.window || s.views.length !== 2) return "needs the array views piles and speeds";
  const top = Math.max(...piles);
  if (p.cells.some((c, i) => c.v !== piles[i]) || sp.cells.length !== top || sp.cells.some((c, k) => c.v !== k + 1)) return "piles must be the input and speeds must run from 1 to the biggest pile";
  const low = sp.window.lo + 1, high = sp.window.hi + 1;
  if (!(1 <= low && low <= high && high <= top)) return `low ${low} and high ${high} are out of order`;
  const time = (v: number) => sum(perPile(piles, v));
  // high always works; the speed just under low never does.
  if (time(high) > hours) return `high (${high}) is not fast enough`;
  if (low > 1 && time(low - 1) <= hours) return `a speed below low (${low - 1}) is fast enough`;
  const speed = varOf(s, "speed");
  if (typeof speed === "number" && varOf(s, "needs") !== time(speed)) return "needs is not the hours the piles take at this speed";
  if (isLast !== (s.line === 9) || (isLast && low !== high)) return "the trace must end on 'return low', when low meets high";
  return sayOk(input, s, prev, [1, low, high, ...(typeof speed === "number" ? perPile(piles, speed) : [])]);
}

export const binarySearchOnAnswers: Pattern = {
  id: "binary-search-on-answers",
  title: "Binary search on answers",
  blurb: "No sorted array in sight: binary search the range of possible answers instead.",
  problem: "Find the slowest speed (bananas an hour, one pile at a time) that eats every pile in time.",
  section: "Binary search",
  tier: "paid",
  pseudocode,
  fields: [
    { name: "piles", label: "Piles", kind: "ints", min: 1, max: 11, minLen: 1, maxLen: 6 },
    { name: "hours", label: "Hours", kind: "int", min: 1, max: 40 },
  ],
  example: { piles: [3, 6, 7, 11], hours: 8 },
  validate: (input) => ((input.hours as number) < (input.piles as number[]).length ? "Each pile takes at least an hour, so hours can't be less than the number of piles." : null),
  random(rng) {
    const piles = list(rng, pick(rng, 3, 5), 2, 11);
    return { piles, hours: piles.length + pick(rng, 0, 6) };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => `The slowest speed that finishes in time: ${a}`,
};
