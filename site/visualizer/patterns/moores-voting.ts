// Moore's voting: the number that fills more than half the array (LeetCode 169, post 14).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { arrayOf, pointerAt, varOf } from "../schema.ts";
import { arr, pick, ptrs, sayOk, step, tiles } from "./_lib.ts";

const pseudocode = [
  "function majorityElement(nums):",
  "    candidate = none",
  "    count = 0",
  "    for each x in nums:",
  "        if count == 0:",
  "            candidate = x   // new candidate",
  "        if x == candidate:",
  "            count = count + 1",
  "        else:",
  "            count = count - 1",
  "    return candidate",
];

const majority = (nums: number[]) => nums.find((v) => nums.filter((x) => x === v).length * 2 > nums.length);

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const n = nums.length;
  let candidate: number | "" = "";
  let count = 0, done = 0;
  const snap = (line: number, say: string, focus = -1) =>
    step(line, say, [arr("nums", tiles(nums), (i) => (i === focus ? "gold" : i < done ? "dim" : "plain"), ptrs(n, { x: focus }))], { candidate, count });

  yield snap(2, "No candidate yet. count starts at 0.");
  for (let i = 0; i < n; i++) {
    const x = nums[i];
    if (count === 0) {
      candidate = x;
      yield snap(5, `count is 0, so ${x} becomes the new candidate.`, i);
    }
    if (x === candidate) {
      count++;
      yield snap(7, `${x} is the candidate: a vote for it. count = ${count}.`, i);
    } else {
      count--;
      yield snap(9, `${x} is not the candidate ${candidate}: it cancels a vote. count = ${count}.`, i);
    }
    done = i + 1;
  }
  yield snap(10, `Every number has voted. The candidate left standing is ${candidate}.`);
  return candidate === "" ? null : candidate;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const a = arrayOf(s, "nums");
  if (!a || s.views.length !== 1) return "needs exactly the array view nums";
  if (a.cells.some((c, i) => c.v !== nums[i] || c.id !== `c${i}`)) return "the cells must stay as the input";
  const x = pointerAt(s, "x");
  if ((x === undefined) !== (s.line === 2 || s.line === 10)) return "the pointer x is on a number exactly while the loop runs";
  // Replay the votes of the numbers already counted.
  const counted = s.line === 2 ? 0 : s.line === 10 ? nums.length : x! + (s.line === 5 ? 0 : 1);
  let cand: number | "" = "";
  let votes = 0;
  for (const v of nums.slice(0, counted)) {
    if (votes === 0) cand = v;
    votes += v === cand ? 1 : -1;
  }
  if (s.line === 5) {
    if (votes !== 0 || varOf(s, "candidate") !== nums[x!] || varOf(s, "count") !== 0) return "a new candidate is picked only when count is 0";
  } else if (varOf(s, "candidate") !== cand || varOf(s, "count") !== votes) {
    return `after ${counted} numbers the candidate is ${cand} with count ${votes}, the step shows ${varOf(s, "candidate")} and ${varOf(s, "count")}`;
  }
  if (isLast !== (s.line === 10)) return "the trace must end on 'return candidate'";
  if (isLast && majority(nums) !== undefined && cand !== majority(nums)) return "the candidate left is not the majority number";
  return sayOk(input, s, prev);
}

export const mooresVoting: Pattern = {
  id: "moores-voting",
  title: "Moore's voting",
  blurb: "One number fills more than half the array: let the numbers vote each other out.",
  problem: "Find the number that appears more than half the time.",
  section: "Arrays and hashing",
  tier: "paid",
  post: "moores-voting",
  pseudocode,
  fields: [{ name: "nums", label: "Numbers", kind: "ints", min: -99, max: 99, minLen: 1, maxLen: 10 }],
  example: { nums: [2, 2, 1, 1, 1, 2, 2] },
  validate: (input) => (majority(input.nums as number[]) === undefined ? "One number must appear more than half the time." : null),
  random(rng) {
    const n = pick(rng, 5, 9);
    const major = pick(rng, 1, 9);
    const nums = Array.from({ length: n }, (_, i) => (i <= n / 2 ? major : pick(rng, 1, 9)));
    for (let i = n - 1; i > 0; i--) {
      const j = pick(rng, 0, i);
      [nums[i], nums[j]] = [nums[j], nums[i]];
    }
    return { nums };
  },
  run,
  check,
  // Without a majority number (never the case for a reader's input) any candidate counts.
  sameAnswer: (_i, got, expected) => expected === null || got === expected,
  answerText: (a) => `The majority number is ${a}`,
};
