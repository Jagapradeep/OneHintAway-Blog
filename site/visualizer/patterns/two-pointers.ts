// Two pointers on a sorted array: find the pair that adds up to the target
// (LeetCode 167). Mirrors post-kit/viz/two-pointers/ref.py step for step.
import type { Answer, Cell, Input, Pattern, Step } from "../schema.ts";
import { pointerAt, strayNumber, varOf } from "../schema.ts";

const pseudocode = [
  "function twoSum(numbers, target):",
  "    left = 0",
  "    right = length(numbers) - 1",
  "    while left < right:",
  "        total = numbers[left] + numbers[right]",
  "        if total == target:",
  "            return [left + 1, right + 1]",
  "        else if total < target:",
  "            left = left + 1",
  "        else:",
  "            right = right - 1",
  "    return none",
];

const L_START = 2, L_TOTAL = 4, L_FOUND = 6, L_LEFT = 8, L_RIGHT = 10, L_NONE = 11;

function cellsFor(nums: number[], left: number, right: number, found: boolean): Cell[] {
  return nums.map((v, i) => ({
    v,
    state: i === left || i === right ? "gold" : i < left || i > right || found ? "dim" : "plain",
  }));
}

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.numbers as number[];
  const target = input.target as number;
  let left = 0;
  let right = nums.length - 1;
  const snap = (line: number, say: string, total: number | string): Step => ({
    line,
    say,
    cells: cellsFor(nums, left, right, line === L_FOUND),
    pointers: nums.length === 0 ? [] : [
      { id: "left", label: "left", at: left },
      { id: "right", label: "right", at: right },
    ],
    vars: [{ name: "target", value: target }, { name: "total", value: total }],
  });

  if (nums.length === 0) {
    yield snap(L_NONE, `There are no numbers, so no pair adds up to ${target}.`, "");
    return null;
  }
  yield snap(L_START, "left starts on the first number, right on the last.", "");
  while (left < right) {
    const total = nums[left] + nums[right];
    yield snap(L_TOTAL, `Add the two ends: ${nums[left]} + ${nums[right]} = ${total}.`, total);
    if (total === target) {
      yield snap(L_FOUND, `${total} is the target. Found it: positions ${left + 1} and ${right + 1}.`, total);
      return [left + 1, right + 1];
    } else if (total < target) {
      left = left + 1;
      yield snap(L_LEFT, `${total} is less than ${target}: too small, so left moves one step in.`, total);
    } else {
      right = right - 1;
      yield snap(L_RIGHT, `${total} is more than ${target}: too big, so right moves one step in.`, total);
    }
  }
  yield snap(L_NONE, `left and right have met. No pair adds up to ${target}.`, "");
  return null;
}

function check(input: Input, step: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.numbers as number[];
  const target = input.target as number;
  if (varOf(step, "target") !== target) return "target changed";
  const total = varOf(step, "total");
  if (nums.length === 0) return step.pointers.length === 0 && step.line === L_NONE ? null : "an empty array must go straight to 'return none'";

  const l = pointerAt(step, "left");
  const r = pointerAt(step, "right");
  if (l === undefined || r === undefined || step.pointers.length !== 2) return "needs exactly the pointers left and right";
  if (l > r) return `left (${l}) has passed right (${r})`;
  const want = cellsFor(nums, l, r, step.line === L_FOUND);
  for (const [i, c] of step.cells.entries()) {
    if (c.v !== nums[i]) return `cell ${i} shows ${c.v}, the input has ${nums[i]}`;
    if (c.state !== want[i].state) return `cell ${i} is ${c.state}, expected ${want[i].state}`;
  }
  const pl = prev ? pointerAt(prev, "left")! : 0;
  const pr = prev ? pointerAt(prev, "right")! : nums.length - 1;
  const moved = `${l - pl},${r - pr}`;
  switch (step.line) {
    case L_START:
      if (prev || l !== 0 || r !== nums.length - 1 || total !== "") return "the first step must put left and right on the two ends";
      break;
    case L_TOTAL:
      if (moved !== "0,0" || l >= r) return "pointers must not move while adding";
      if (total !== nums[l] + nums[r]) return `total ${total} is not ${nums[l]} + ${nums[r]}`;
      break;
    case L_FOUND:
      if (moved !== "0,0" || total !== target || nums[l] + nums[r] !== target || l >= r) return "'found' without a pair that adds up to the target";
      if (!isLast) return "steps continue after the answer";
      break;
    case L_LEFT:
      if (moved !== "1,0") return "only left may move, one step right";
      if (total !== nums[l - 1] + nums[r] || (total as number) >= target) return "left moved although the total was not too small";
      break;
    case L_RIGHT:
      if (moved !== "0,-1") return "only right may move, one step left";
      if (total !== nums[l] + nums[r + 1] || (total as number) <= target) return "right moved although the total was not too big";
      break;
    case L_NONE:
      if (l !== r || moved !== "0,0" || !isLast || total !== "") return "'return none' before the pointers met";
      break;
    default:
      return `line ${step.line} never gets a step`;
  }
  if (isLast && step.line !== L_FOUND && step.line !== L_NONE) return "the trace stops without an answer";
  const facts = [target, nums[l], nums[r], l + 1, r + 1];
  if (typeof total === "number") facts.push(total);
  return strayNumber(step.say, facts);
}

function sameAnswer(input: Input, got: Answer, expected: Answer): boolean {
  if (got === null || expected === null) return got === expected;
  // More than one pair can add up to the target, so any correct pair counts.
  const nums = input.numbers as number[];
  if (!Array.isArray(got) || got.length !== 2) return false;
  const [a, b] = got;
  return Number.isInteger(a) && Number.isInteger(b) && a >= 1 && a < b && b <= nums.length && nums[a - 1] + nums[b - 1] === input.target;
}

function random(rng: () => number): Input {
  const n = 5 + Math.floor(rng() * 4);
  const numbers: number[] = [];
  let v = Math.floor(rng() * 4);
  for (let i = 0; i < n; i++) {
    v += 1 + Math.floor(rng() * 4);
    numbers.push(v);
  }
  const i = Math.floor(rng() * n);
  let j = Math.floor(rng() * (n - 1));
  if (j >= i) j++;
  // Usually a real pair; now and then a target nothing reaches.
  const target = rng() < 0.8 ? numbers[i] + numbers[j] : numbers[n - 1] + numbers[n - 2] + 1;
  return { numbers, target };
}

export const twoPointers: Pattern = {
  id: "two-pointers",
  title: "Two pointers",
  blurb: "A sorted array and a pair to find: start at both ends and walk inward.",
  problem: "Find the two numbers in a sorted array that add up to the target.",
  section: "Arrays and hashing",
  tier: "free",
  post: "two-pointers",
  pseudocode,
  fields: [
    { name: "numbers", label: "Sorted numbers", kind: "ints", min: -99, max: 99, minLen: 2, maxLen: 10 },
    { name: "target", label: "Target", kind: "int", min: -198, max: 198 },
  ],
  example: { numbers: [1, 3, 4, 6, 8, 11], target: 10 },
  validate(input) {
    const nums = input.numbers as number[];
    for (let i = 1; i < nums.length; i++) {
      if (nums[i] < nums[i - 1]) return `The numbers must be sorted from small to large: ${nums[i]} comes after ${nums[i - 1]}.`;
    }
    return null;
  },
  random,
  run,
  check,
  sameAnswer,
  answerText: (a) => (Array.isArray(a) ? `Positions ${a[0]} and ${a[1]} (counted from 1)` : "No pair adds up to the target"),
};
