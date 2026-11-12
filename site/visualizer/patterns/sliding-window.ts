// Sliding window of any size: the longest run of numbers whose total stays
// within the budget (post 08). Mirrors post-kit/viz/sliding-window/ref.py.
import type { Answer, CellState, Input, Pattern, Step } from "../schema.ts";
import { pointerAt, strayNumber, varOf } from "../schema.ts";

const pseudocode = [
  "function longestWithin(nums, budget):",
  "    left = 0",
  "    total = 0",
  "    best = 0",
  "    for right from 0 to length(nums) - 1:",
  "        total = total + nums[right]",
  "        while total > budget:",
  "            total = total - nums[left]",
  "            left = left + 1",
  "        best = max(best, right - left + 1)",
  "    return best",
];

const L_START = 3, L_GROW = 5, L_SHRINK = 8, L_MEASURE = 9, L_DONE = 10;

/** Before the window: dim. In it: steel, with the number that just joined gold.
 *  The last step shows the best window in gold and dims the rest. */
function stateFor(i: number, lo: number, hi: number, line: number): CellState {
  if (line === L_DONE) return i >= lo && i <= hi ? "gold" : "dim";
  if (i < lo) return "dim";
  if (i > hi) return "plain";
  return line === L_GROW && i === hi ? "gold" : "steel";
}

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const budget = input.budget as number;
  let left = 0, right = -1, total = 0, best = 0, bestLeft = 0;
  const snap = (line: number, say: string): Step => {
    const done = line === L_DONE;
    const lo = done ? bestLeft : left;
    const hi = done ? bestLeft + best - 1 : right;
    let shown = total;
    if (done) {
      shown = 0;
      for (let i = lo; i <= hi; i++) shown += nums[i];
    }
    const pointers = [];
    if (!done && left < nums.length) pointers.push({ id: "left", label: "left", at: left });
    if (!done && right >= 0) pointers.push({ id: "right", label: "right", at: right });
    return {
      line,
      say,
      cells: nums.map((v, i) => ({ v, state: stateFor(i, lo, hi, line) })),
      pointers,
      window: { lo, hi },
      vars: [{ name: "budget", value: budget }, { name: "total", value: shown }, { name: "best", value: best }],
    };
  };

  if (nums.length === 0) {
    yield snap(L_DONE, "There are no numbers, so the longest window is 0.");
    return 0;
  }
  yield snap(L_START, "The window starts empty: total 0, best 0.");
  for (right = 0; right < nums.length; right++) {
    total = total + nums[right];
    yield snap(L_GROW, `${nums[right]} joins the window: total is ${total}.`);
    while (total > budget) {
      const before = total;
      total = total - nums[left];
      left = left + 1;
      yield snap(L_SHRINK, `${before} is over the budget ${budget}, so ${nums[left - 1]} leaves: total is ${total}.`);
    }
    const length = right - left + 1;
    if (length > best) {
      best = length;
      bestLeft = left;
      yield snap(L_MEASURE, `The window fits. Its length is ${length}: a new best.`);
    } else {
      yield snap(L_MEASURE, `The window fits. Its length is ${length}, so best stays ${best}.`);
    }
  }
  right = nums.length - 1;
  yield snap(L_DONE, `Every number has joined once. The longest window that fits has length ${best}.`);
  return best;
}

function check(input: Input, step: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const budget = input.budget as number;
  const n = nums.length;
  const w = step.window;
  if (!w) return "no window";
  const { lo, hi } = w;
  const len = hi - lo + 1;
  const total = varOf(step, "total");
  const best = varOf(step, "best");
  if (varOf(step, "budget") !== budget) return "budget changed";
  if (typeof total !== "number" || typeof best !== "number") return "total and best must be numbers";
  let sum = 0;
  for (let i = lo; i <= hi; i++) sum += nums[i];
  if (sum !== total) return `total says ${total}, the window ${lo}..${hi} adds up to ${sum}`;
  for (const [i, c] of step.cells.entries()) {
    if (c.v !== nums[i]) return `cell ${i} shows ${c.v}, the input has ${nums[i]}`;
    const want = stateFor(i, lo, hi, step.line);
    if (c.state !== want) return `cell ${i} is ${c.state}, expected ${want}`;
  }
  const pBest = prev ? (varOf(prev, "best") as number) : 0;
  const pTotal = prev ? (varOf(prev, "total") as number) : 0;
  const pLo = prev?.window ? prev.window.lo : 0;
  const pHi = prev?.window ? prev.window.hi : -1;
  const facts = [budget, total, best, len, 0];

  if (step.line === L_DONE) {
    if (!isLast) return "steps continue after 'return best'";
    if (step.pointers.length) return "the last step shows no pointers";
    if (len !== best || best !== pBest) return `the last step must show the best window (length ${pBest})`;
    if (total > budget && len > 0) return "the best window is over the budget";
    if (prev && pHi !== n - 1) return "'return best' before right reached the end";
    return strayNumber(step.say, facts);
  }
  if (isLast) return "the trace stops before 'return best'";
  if (pointerAt(step, "left") !== (lo < n ? lo : undefined)) return "the left pointer is not on the window's first cell";
  if (pointerAt(step, "right") !== (hi >= 0 ? hi : undefined)) return "the right pointer is not on the window's last cell";
  if (step.pointers.length !== (lo < n ? 1 : 0) + (hi >= 0 ? 1 : 0)) return "only left and right may be shown";
  switch (step.line) {
    case L_START:
      if (prev || lo !== 0 || hi !== -1 || best !== 0) return "the first step must be an empty window";
      break;
    case L_GROW:
      if (lo !== pLo || hi !== pHi + 1 || best !== pBest) return "growing must move only right, by one";
      if (prev && prev.line !== L_START && prev.line !== L_MEASURE) return "a number joined before the last window was measured";
      facts.push(nums[hi]);
      break;
    case L_SHRINK:
      if (lo !== pLo + 1 || hi !== pHi || best !== pBest) return "shrinking must move only left, by one";
      if (pTotal <= budget) return "the window shrank although it was within the budget";
      facts.push(pTotal, nums[lo - 1]);
      break;
    case L_MEASURE:
      if (lo !== pLo || hi !== pHi) return "the window moved while it was measured";
      if (total > budget) return `measured a window that is over the budget (${total} > ${budget})`;
      if (best !== Math.max(pBest, len)) return `best is ${best}, expected ${Math.max(pBest, len)}`;
      break;
    default:
      return `line ${step.line} never gets a step`;
  }
  return strayNumber(step.say, facts);
}

function random(rng: () => number): Input {
  const n = 5 + Math.floor(rng() * 4);
  const nums = Array.from({ length: n }, () => 1 + Math.floor(rng() * 9));
  return { nums, budget: 5 + Math.floor(rng() * 11) };
}

export const slidingWindow: Pattern = {
  id: "sliding-window",
  title: "Sliding window",
  blurb: "The longest stretch in a row that follows a rule: grow on the right, shrink on the left.",
  problem: "Find the longest run of numbers in a row whose total is at most the budget.",
  section: "Arrays and hashing",
  tier: "free",
  post: "sliding-window-any-size",
  pseudocode,
  fields: [
    { name: "nums", label: "Numbers", kind: "ints", min: 1, max: 99, minLen: 1, maxLen: 10 },
    { name: "budget", label: "Budget", kind: "int", min: 0, max: 999 },
  ],
  example: { nums: [2, 1, 3, 1, 4], budget: 5 },
  validate(input) {
    if ((input.nums as number[]).some((v) => v < 1)) return "Every number must be 1 or more: the window only works with positive numbers.";
    if ((input.budget as number) < 0) return "The budget can't be below 0.";
    return null;
  },
  random,
  run,
  check,
  sameAnswer: (_input, got, expected) => got === expected,
  answerText: (a) => `Longest window that fits: ${a}`,
};
