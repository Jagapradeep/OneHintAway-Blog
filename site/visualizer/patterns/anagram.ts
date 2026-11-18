// The frequency array: count one word up and the other down in 26 boxes (post 36).
// The post's pseudocode also holds isPalindrome; the player walks isAnagram, the
// post's main technique. Only the boxes of letters that appear are drawn: the other
// boxes stay 0 throughout.
import type { Answer, ArrayView, Input, MapView, Pattern, Step } from "../schema.ts";
import { arr, sayOk, step, tiles } from "./_lib.ts";

const pseudocode = [
  "function isPalindrome(word):",
  "    left = 0",
  "    right = length(word) - 1",
  "    while left < right:",
  "        if word[left] != word[right]:",
  "            return false",
  "        left = left + 1",
  "        right = right - 1",
  "    return true",
  "",
  "function isAnagram(s, t):",
  "    counts = array of 26 zeros",
  "    for each letter in s:",
  "        k = alphabet index of letter",
  "        counts[k] = counts[k] + 1",
  "    for each letter in t:",
  "        k = alphabet index of letter",
  "        counts[k] = counts[k] - 1",
  "    for each count in counts:",
  "        if count != 0:",
  "            return false",
  "    return true",
];

const lettersOf = (s: string, t: string) => [...new Set(s + t)].sort();

function* run(input: Input): Generator<Step, Answer, void> {
  const s = (input.s as string).toLowerCase(), t = (input.t as string).toLowerCase();
  const used = lettersOf(s, t);
  const count: Record<string, number> = Object.fromEntries(used.map((ch) => [ch, 0]));
  const ts = tiles([...s]), tt = tiles([...t]);
  let inS = -1, inT = -1, doneS = 0, doneT = 0, box = "";
  const lit = (at: number, done: number) => (i: number) => (i === at ? "gold" : i < done ? "steel" : "plain");
  const snap = (line: number, say: string) =>
    step(line, say, [
      arr("s", ts, lit(inS, doneS), [], { label: "s", hideIndex: true }),
      arr("t", tt, lit(inT, doneT), [], { label: "t", hideIndex: true }),
      { kind: "map", id: "counts", label: "Counts, one box per letter used", entries: used.map((ch) => ({ id: ch, k: ch, v: count[ch], state: ch === box ? "gold" : count[ch] === 0 ? "plain" : "steel" })) } as MapView,
    ]);

  yield snap(11, `26 boxes, all 0. Only the boxes for ${used.join(", ")} will change.`);
  for (const [i, ch] of [...s].entries()) {
    inS = i;
    doneS = i + 1;
    box = ch;
    count[ch]++;
    yield snap(14, `${ch} from s: box ${ch} goes up to ${count[ch]}.`);
  }
  inS = -1;
  for (const [i, ch] of [...t].entries()) {
    inT = i;
    doneT = i + 1;
    box = ch;
    count[ch]--;
    yield snap(17, `${ch} from t: box ${ch} goes down to ${count[ch]}.`);
  }
  inT = -1;
  for (const ch of used) {
    box = ch;
    if (count[ch] !== 0) {
      yield snap(20, `Box ${ch} is ${count[ch]}, not 0: ${count[ch] > 0 ? "s has" : "t has"} more ${ch}'s. Return false.`);
      return false;
    }
    yield snap(19, `Box ${ch} is 0.`);
  }
  box = "";
  yield snap(21, "Every box is back at 0: the words use the same letters. Return true.");
  return true;
}

function check(input: Input, st: Step, prev: Step | null, isLast: boolean): string | null {
  const s = (input.s as string).toLowerCase(), t = (input.t as string).toLowerCase();
  const [vs, vt, vm] = st.views as [ArrayView, ArrayView, MapView];
  if (st.views.length !== 3 || vs.id !== "s" || vt.id !== "t" || vm?.kind !== "map") return "needs the arrays s and t and the map of counts";
  if (vs.cells.map((c) => c.v).join("") !== s || vt.cells.map((c) => c.v).join("") !== t) return "the two words must be the input";
  // How far each word has been counted, read from the picture.
  const doneS = vs.cells.filter((c) => c.state !== "plain").length;
  const doneT = vt.cells.filter((c) => c.state !== "plain").length;
  if (doneT > 0 && doneS !== s.length) return "t is counted only after the whole of s";
  const used = lettersOf(s, t);
  if (vm.entries.map((e) => e.k).join("") !== used.join("")) return "one box per letter used, in alphabet order";
  for (const e of vm.entries) {
    const up = [...s.slice(0, doneS)].filter((c) => c === e.k).length;
    const down = [...t.slice(0, doneT)].filter((c) => c === e.k).length;
    if (e.v !== up - down) return `box ${e.k} shows ${e.v}, counting gives ${up - down}`;
  }
  if (st.line === 20 && vm.entries.find((e) => e.state === "gold")?.v === 0) return "'return false' on a box that is 0";
  if (st.line === 21 && vm.entries.some((e) => e.v !== 0)) return "'return true' with a box that is not 0";
  if (isLast !== (st.line === 20 || st.line === 21)) return "the trace must end on a return line";
  return sayOk(input, st, prev, [26, 0]);
}

export const anagram: Pattern = {
  id: "anagram",
  title: "Frequency count",
  blurb: "Count one word up and the other down in 26 boxes: all 0 means the same letters.",
  problem: "Do the two words use exactly the same letters, as many times each?",
  section: "2D arrays and strings",
  tier: "paid",
  pseudocode,
  fields: [
    { name: "s", label: "Word s", kind: "text", min: 0, max: 0, minLen: 1, maxLen: 8 },
    { name: "t", label: "Word t", kind: "text", min: 0, max: 0, minLen: 1, maxLen: 8 },
  ],
  example: { s: "stone", t: "notes" },
  validate: () => null,
  random(rng) {
    const words = [["stone", "notes"], ["listen", "silent"], ["below", "elbow"], ["night", "thing"], ["stone", "note"], ["rat", "car"], ["state", "taste"], ["apple", "paper"]];
    const [s, t] = words[Math.floor(rng() * words.length)];
    return { s, t };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => (a ? "Same letters: true" : "Not the same letters: false"),
};
