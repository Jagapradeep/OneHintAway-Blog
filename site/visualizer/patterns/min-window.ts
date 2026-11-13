// Minimum window substring: the shortest piece of s holding every letter of t (LeetCode 76, post 09).
import type { Answer, Input, NodeState, Pattern, Step } from "../schema.ts";
import { arrayOf, mapOf, varOf } from "../schema.ts";
import { arr, pick, sayOk, step, tiles } from "./_lib.ts";

const pseudocode = [
  "function minWindow(s, t):",
  "    need = empty map   // default 0",
  "    for each c in t:",
  "        need[c] = need[c] + 1",
  "    missing = length(t)",
  "    left = 0",
  "    bestStart = 0",
  "    bestLen = infinity",
  "    for right from 0 to length(s) - 1:",
  "        c = s[right]",
  "        if need[c] > 0:",
  "            missing = missing - 1",
  "        need[c] = need[c] - 1",
  "        while missing == 0:",
  "            if right - left + 1 < bestLen:",
  "                bestStart = left",
  "                bestLen = right - left + 1",
  "            d = s[left]",
  "            need[d] = need[d] + 1",
  "            if need[d] > 0:",
  "                missing = missing + 1",
  "            left = left + 1",
  "    if bestLen == infinity:",
  '        return ""',
  "    return s from bestStart, bestLen letters",
];

const count = (text: string) => {
  const m: Record<string, number> = {};
  for (const c of text) m[c] = (m[c] ?? 0) + 1;
  return m;
};
/** How many letters of t the piece still lacks. */
function lacking(piece: string, t: string): number {
  const have = count(piece);
  return Object.entries(count(t)).reduce((n, [c, k]) => n + Math.max(0, k - (have[c] ?? 0)), 0);
}

function* run(input: Input): Generator<Step, Answer, void> {
  const s = input.s as string;
  const t = input.t as string;
  const need = new Map<string, number>();
  for (const c of t) need.set(c, (need.get(c) ?? 0) + 1);
  let missing = t.length, left = 0, right = -1, bestStart = 0, hot = "";
  let bestLen: number | "" = "";
  const snap = (line: number, say: string, focus = -1) =>
    step(
      line,
      say,
      [
        arr("s", tiles([...s]), (i) => (i === focus ? "gold" : i >= left && i <= right ? "plain" : "dim"), [], { window: { lo: left, hi: right } }),
        {
          kind: "map",
          id: "need",
          label: "need · letters the window still owes",
          entries: [...need].map(([k, v]) => ({ id: `k${k}`, k, v, state: (k === hot ? "gold" : v > 0 ? "plain" : "dim") as NodeState })),
        },
      ],
      { missing, best: bestLen === "" ? "" : s.slice(bestStart, bestStart + bestLen) },
    );

  yield snap(7, `need counts the letters of t. All ${missing} are still missing.`);
  for (right = 0; right < s.length; right++) {
    const c = s[right];
    const was = need.get(c) ?? 0;
    if (was > 0) missing--;
    need.set(c, was - 1);
    hot = c;
    yield snap(12, was > 0 ? `${c} is needed: take it. missing = ${missing}.` : `${c} is not needed right now. missing stays ${missing}.`, right);
    while (missing === 0) {
      const len = right - left + 1;
      if (bestLen === "" || len < bestLen) {
        bestStart = left;
        bestLen = len;
        hot = "";
        yield snap(16, `Nothing is missing: this window of ${len} is the shortest so far.`);
      }
      const d = s[left];
      need.set(d, need.get(d)! + 1);
      if (need.get(d)! > 0) missing++;
      left++;
      hot = d;
      yield snap(21, missing > 0 ? `Drop ${d} from the left: now a ${d} is missing again.` : `Drop ${d} from the left: the window still holds every letter.`);
    }
  }
  right = s.length - 1;
  hot = "";
  if (bestLen === "") {
    yield snap(23, "No window ever held every letter of t: return an empty string.");
    return "";
  }
  const best = s.slice(bestStart, bestStart + bestLen);
  yield snap(24, `The shortest window is ${best}, ${bestLen} letters long.`);
  return best;
}

function check(input: Input, st: Step, prev: Step | null, isLast: boolean): string | null {
  const s = input.s as string;
  const t = input.t as string;
  const a = arrayOf(st, "s");
  const m = mapOf(st, "need");
  if (!a?.window || !m || st.views.length !== 2) return "needs the array view s with a window, and the map view need";
  const { lo, hi } = a.window;
  if (a.cells.map((c) => c.v).join("") !== s) return "the cells must spell s";
  const piece = s.slice(lo, hi + 1);
  if (varOf(st, "missing") !== lacking(piece, t)) return `missing is ${varOf(st, "missing")}, the window lacks ${lacking(piece, t)}`;
  const inT = count(t);
  const inWin = count(piece);
  for (const e of m.entries) {
    const want = (inT[e.k] ?? 0) - (inWin[e.k] ?? 0);
    if (e.v !== want) return `need[${e.k}] is ${e.v}, expected ${want}`;
  }
  for (const c of Object.keys(inT)) if (!m.entries.some((e) => e.k === c)) return `need has no entry for ${c}`;
  const best = varOf(st, "best") as string;
  if (best !== "" && (!s.includes(best) || lacking(best, t) !== 0)) return `best "${best}" is not a piece of s with every letter of t`;
  if (isLast !== (st.line === 23 || st.line === 24)) return "the trace must end on a return line";
  if (isLast && (st.line === 23) !== (best === "")) return "the wrong return line";
  return sayOk(input, st, prev, [t.length, hi - lo + 1, best.length]);
}

export const minWindow: Pattern = {
  id: "min-window",
  title: "Minimum window substring",
  blurb: "The shortest piece of text holding every wanted letter: grow on the right, shrink on the left.",
  problem: "Find the shortest piece of s that holds every letter of t.",
  section: "Arrays and hashing",
  tier: "paid",
  post: "minimum-window-substring",
  pseudocode,
  fields: [
    { name: "s", label: "Text s", kind: "text", min: 0, max: 0, minLen: 1, maxLen: 10 },
    { name: "t", label: "Letters t", kind: "text", min: 0, max: 0, minLen: 1, maxLen: 4 },
  ],
  example: { s: "ADOBECBA", t: "ABC" },
  validate: () => null,
  random(rng) {
    const s = Array.from({ length: pick(rng, 7, 10) }, () => "ABCDE"[pick(rng, 0, 4)]).join("");
    const t = Array.from({ length: pick(rng, 2, 3) }, () => (rng() < 0.9 ? s[pick(rng, 0, s.length - 1)] : "F")).join("");
    return { s, t };
  },
  run,
  check,
  // Two windows can tie for shortest: any piece of s of that length with every letter counts.
  sameAnswer: (input, got, expected) =>
    typeof got === "string" && typeof expected === "string" && got.length === expected.length && (got === "" || ((input.s as string).includes(got) && lacking(got, input.t as string) === 0)),
  answerText: (a) => (a === "" ? "No window holds every letter" : `Shortest window: ${a}`),
};
