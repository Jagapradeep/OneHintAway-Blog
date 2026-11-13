// Recursion: factorial as a call stack that grows down to the base case and unwinds (post 21).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { stackOf, varOf } from "../schema.ts";
import { pick, sayOk, step } from "./_lib.ts";

const pseudocode = ["function factorial(n):", "    if n == 0:", "        return 1  // base case", "    return n * factorial(n - 1)"];

const fact = (k: number): number => (k <= 1 ? 1 : k * fact(k - 1));

function* run(input: Input): Generator<Step, Answer, void> {
  const n = input.n as number;
  const calls: number[] = []; // the n of every call still waiting, newest last
  const snap = (line: number, say: string, result: number | "") =>
    step(line, say, [{ kind: "stack", id: "calls", label: "Call stack", items: calls.map((k) => ({ id: `f${k}`, v: `f(${k})` })) }], { n: calls[calls.length - 1], result });

  for (let k = n; k >= 0; k--) {
    calls.push(k);
    if (k === 0) yield snap(2, "factorial(0) is the base case: it returns 1 without calling anyone.", 1);
    else yield snap(3, `factorial(${k}) needs factorial(${k - 1}) first, so it waits on the stack.`, "");
  }
  let result = 1;
  for (let k = 1; k <= n; k++) {
    calls.pop();
    result *= k;
    yield snap(3, `factorial(${k - 1}) returned ${result / k}, so factorial(${k}) returns ${k} × ${result / k} = ${result}.`, result);
  }
  return result;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const n = input.n as number;
  const st = stackOf(s, "calls");
  if (!st || s.views.length !== 1 || st.items.length === 0) return "needs exactly the stack view calls, never empty";
  // The stack is factorial(n) at the bottom, then n - 1, n - 2, … with nothing skipped.
  if (st.items.some((it, k) => it.id !== `f${n - k}` || it.v !== `f(${n - k})`)) return "the calls on the stack must count down from n without a gap";
  const top = n - st.items.length + 1;
  if (varOf(s, "n") !== top) return "n must be the n of the call on top";
  const result = varOf(s, "result");
  if (result !== "" && result !== fact(top)) return `the call on top returns ${fact(top)}, the step shows ${result}`;
  if ((s.line === 2) !== (top === 0 && result === 1 && (prev === null || varOf(prev, "result") === ""))) return "'return 1' is the step where the base case is reached";
  if (prev && st.items.length !== stackOf(prev, "calls")!.items.length + (result === "" || s.line === 2 ? 1 : -1)) return "each step pushes one call or pops one";
  if (isLast !== (st.items.length === 1 && result !== "")) return "the trace ends when the first call returns";
  return sayOk(input, s, prev, [...Array(n + 1).keys(), ...Array.from({ length: n + 1 }, (_, k) => fact(k))]);
}

export const recursion: Pattern = {
  id: "recursion",
  title: "Recursion",
  blurb: "A function that calls itself: watch the calls stack up, hit the base case, and unwind.",
  problem: "Compute n factorial: n × (n - 1) × … × 1.",
  section: "Recursion and sorting",
  tier: "free",
  post: "recursion",
  pseudocode,
  fields: [{ name: "n", label: "n", kind: "int", min: 0, max: 7 }],
  example: { n: 4 },
  validate: () => null,
  random: (rng) => ({ n: pick(rng, 2, 6) }),
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => `The first call returns ${a}`,
};
