// Monotonic stack: the next greater number to the right of each number.
// Mirrors post-kit/viz/monotonic-stack/ref.py step for step.
import type { Answer, CellState, Input, Pattern, StackItem, Step } from "../schema.ts";
import { arrayOf, pointerAt, stackOf, strayNumber, varOf } from "../schema.ts";

const pseudocode = [
  "function nextGreater(nums):",
  "    answer = list of -1, same length as nums",
  "    stack = empty stack",
  "    for i from 0 to length(nums) - 1:",
  "        while stack is not empty and",
  "              nums[top of stack] < nums[i]:",
  "            waiting = pop from stack",
  "            answer[waiting] = nums[i]",
  "        push i onto stack",
  "    return answer",
];

const L_START = 2, L_POP = 7, L_PUSH = 8, L_DONE = 9;

// Two characters per answer, so the line keeps its width as answers arrive.
const show = (answer: number[]) => answer.map((v) => String(v).padStart(2, " ")).join(", ");

/** The number being looked at: gold. Answered: steel. Still waiting: plain,
 *  and dim on the last step, when nothing bigger can come any more. */
function stateFor(i: number, at: number, answer: number[], line: number): CellState {
  if (line !== L_DONE && i === at) return "gold";
  if (answer[i] !== -1) return "steel";
  return line === L_DONE ? "dim" : "plain";
}

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const answer: number[] = nums.map(() => -1);
  const stack: number[] = [];
  let at = -1;
  const snap = (line: number, say: string): Step => ({
    line,
    say,
    views: [
      {
        kind: "array",
        id: "nums",
        cells: nums.map((v, i) => ({ id: `c${i}`, v, state: stateFor(i, at, answer, line) })),
        pointers: line === L_DONE || at < 0 ? [] : [{ id: "i", label: "i", at }],
      },
      { kind: "stack", id: "stack", items: stack.map((j) => ({ id: `s${j}`, v: nums[j], from: { view: "nums", at: j } })) },
    ],
    vars: [{ name: "answer", value: show(answer) }],
  });

  if (nums.length === 0) {
    yield snap(L_DONE, "There are no numbers, so the answer is empty.");
    return answer;
  }
  yield snap(L_START, "Every answer starts at -1. The stack of waiting numbers is empty.");
  for (let i = 0; i < nums.length; i++) {
    at = i;
    while (stack.length > 0 && nums[stack[stack.length - 1]] < nums[i]) {
      const waiting = stack.pop()!;
      answer[waiting] = nums[i];
      yield snap(L_POP, `${nums[waiting]} was waiting and ${nums[i]} is bigger, so the answer for ${nums[waiting]} is ${nums[i]}.`);
    }
    const say = stack.length === 0
      ? `Nothing is waiting, so ${nums[i]} goes onto the stack to wait.`
      : `${nums[i]} is not bigger than ${nums[stack[stack.length - 1]]}, so ${nums[i]} goes onto the stack to wait.`;
    stack.push(i);
    yield snap(L_PUSH, say);
  }
  yield snap(L_DONE, "Nothing bigger came for the numbers still on the stack: they keep -1.");
  return answer.slice();
}

function check(input: Input, step: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const n = nums.length;
  const arr = arrayOf(step, "nums");
  const stack = stackOf(step, "stack")?.items;
  if (!arr || !stack || step.views.length !== 2) return "needs exactly the array view nums and the stack view stack";
  const fromOf = (it: StackItem) => (it.from?.view === "nums" ? it.from.at : -1);
  const shown = varOf(step, "answer");
  if (typeof shown !== "string") return "the answer must be shown";
  const answer = n === 0 ? [] : shown.split(",").map((s) => Number(s.trim()));
  if (answer.length !== n || answer.some((v) => !Number.isInteger(v)) || shown !== show(answer)) return `the answer line "${shown}" is malformed`;

  // The stack really is monotonic: indexes climb, values never climb.
  for (const [k, it] of stack.entries()) {
    const from = fromOf(it);
    if (from < 0 || it.id !== `s${from}` || it.v !== nums[from]) return `stack item ${k} does not match its cell`;
    if (answer[from] !== -1) return `${it.v} is on the stack but already has an answer`;
    if (k > 0 && (fromOf(stack[k - 1]) >= from ||(stack[k - 1].v as number) < (it.v as number))) return `the stack is not monotonic: ${stack[k - 1].v} sits under ${it.v}`;
  }
  const at = pointerAt(step, "i");
  // Every answer shown is right: a bigger number, with nothing bigger in between.
  for (let j = 0; j < n; j++) {
    if (answer[j] === -1) continue;
    let k = j + 1;
    while (k < n && nums[k] <= nums[j]) k++;
    if (k >= n || nums[k] !== answer[j] || (at !== undefined && k > at)) return `answer[${j}] = ${answer[j]} is not the next greater number seen so far`;
  }
  for (const [i, c] of arr.cells.entries()) {
    if (c.id !== `c${i}`) return `cell ${i} has id ${c.id}: cells never move here`;
    if (c.v !== nums[i]) return `cell ${i} shows ${c.v}, the input has ${nums[i]}`;
    const want = stateFor(i, at ?? -1, answer, step.line);
    if (c.state !== want) return `cell ${i} is ${c.state}, expected ${want}`;
  }
  const pStack: StackItem[] = (prev && stackOf(prev, "stack")?.items) || [];
  const pAt = prev ? pointerAt(prev, "i") ?? -1 : -1;
  const pShown = prev ? varOf(prev, "answer") : show(nums.map(() => -1));
  const ids = (s: StackItem[]) => s.map((x) => x.id).join(" ");
  const facts = [-1];

  if (step.line === L_DONE) {
    if (!isLast || arr.pointers.length) return "'return answer' must be the last step, with no pointer";
    if (prev && (pAt !== n - 1 || prev.line !== L_PUSH)) return "'return answer' before the last number was pushed";
    if (ids(stack) !== ids(pStack) || shown !== pShown) return "the last step changed the stack or the answer";
    return strayNumber(step.say, facts);
  }
  if (isLast) return "the trace stops before 'return answer'";
  if (step.line === L_START) {
    if (prev || stack.length || arr.pointers.length || answer.some((v) => v !== -1)) return "the first step must be an empty stack and all -1";
    return strayNumber(step.say, facts);
  }
  if (at === undefined || arr.pointers.length !== 1) return "needs exactly the pointer i";
  const fresh = prev!.line === L_START || prev!.line === L_PUSH;
  if (at !== (fresh ? pAt + 1 : pAt)) return "i may only step forward by one, after a push";
  if (step.line === L_POP) {
    const top = pStack[pStack.length - 1];
    if (!top || ids(stack) !== ids(pStack.slice(0, -1))) return "a pop must remove exactly the top of the stack";
    if (!((top.v as number) < nums[at])) return `${top.v} was popped although ${nums[at]} is not bigger`;
    if (answer[fromOf(top)] !== nums[at]) return "the popped number did not get its answer";
    facts.push(top.v as number, nums[at]);
  } else if (step.line === L_PUSH) {
    const top = pStack[pStack.length - 1];
    if (ids(stack) !== [...pStack.map((x) => x.id), `s${at}`].join(" ").trim()) return "a push must add exactly the current number";
    if (top && (top.v as number) < nums[at]) return `${nums[at]} was pushed while the smaller ${top.v} was still waiting`;
    if (shown !== pShown) return "a push changed the answer";
    facts.push(nums[at]);
    if (top) facts.push(top.v as number);
  } else {
    return `line ${step.line} never gets a step`;
  }
  return strayNumber(step.say, facts);
}

function random(rng: () => number): Input {
  const n = 5 + Math.floor(rng() * 3);
  return { nums: Array.from({ length: n }, () => 1 + Math.floor(rng() * 9)) };
}

export const monotonicStack: Pattern = {
  id: "monotonic-stack",
  title: "Monotonic stack",
  blurb: "The next bigger number to the right of each number: keep the ones still waiting on a stack.",
  problem: "For each number, find the next number to its right that is bigger (or -1 if there is none).",
  section: "Stack and queue",
  tier: "paid",
  pseudocode,
  fields: [{ name: "nums", label: "Numbers", kind: "ints", min: 0, max: 99, minLen: 1, maxLen: 8 }],
  example: { nums: [2, 1, 5, 3, 6] },
  validate(input) {
    return (input.nums as number[]).some((v) => v < 0) ? "Every number must be 0 or more, because -1 means \"no bigger number\"." : null;
  },
  random,
  run,
  check,
  sameAnswer: (_input, got, expected) => JSON.stringify(got) === JSON.stringify(expected),
  answerText: (a) => `Next greater numbers: ${(a as number[]).join(", ")}`,
};
