// Fast and slow pointers: slow moves 1 node, fast moves 2. They meet if the list
// loops; if fast runs out, slow is on the middle node (post 42). The trace runs
// hasCycle; its loop is middleNode's loop, so a list with no loop ends on the middle.
// The Python twin (post-kit/viz/fast-slow-pointers/ref.py) makes the same steps.
import type { Answer, Input, ListNode, Pattern, Step } from "../schema.ts";
import { listOf, varOf } from "../schema.ts";
import { list, pick, sayOk, step } from "./_lib.ts";

const pseudocode = [
  "function middleNode(head):",
  "    slow = head",
  "    fast = head",
  "    while fast != none and fast.next != none:",
  "        slow = slow.next",
  "        fast = fast.next.next",
  "    return slow",
  "",
  "function hasCycle(head):",
  "    slow = head",
  "    fast = head",
  "    while fast != none and fast.next != none:",
  "        slow = slow.next        // 1 step",
  "        fast = fast.next.next   // 2 steps",
  "        if slow == fast:",
  "            return true   // a loop",
  "    return false",
];

const LABEL = "Linked list";

/** Index of the node after `i`, or -1 for none. */
const after = (n: number, loop: number, i: number) => (i < 0 ? -1 : i + 1 < n ? i + 1 : loop);

function* run(input: Input): Generator<Step, Answer, void> {
  const vals = input.nums as number[];
  const loop = input.loop as number;
  const n = vals.length;
  const nodes = (slow: number, fast: number): ListNode[] =>
    vals.map((v, i) => ({ id: `n${i}`, v, next: after(n, loop, i) < 0 ? null : `n${after(n, loop, i)}`, state: i === slow ? "gold" : i === fast ? "steel" : "plain" }));
  let slow = 0, fast = 0, round = 0;
  const name = (i: number) => (i < 0 ? "none" : String(vals[i]));
  const snap = (line: number, say: string) =>
    step(line, say, [{ kind: "list", id: "list", label: LABEL, nodes: nodes(slow, fast), pointers: [
      { id: "slow", label: "slow", at: slow < 0 ? null : `n${slow}` },
      { id: "fast", label: "fast", at: fast < 0 ? null : `n${fast}` },
    ] }], { round });

  yield snap(10, `slow and fast both start on the head, ${vals[0]}.`);
  while (fast >= 0 && after(n, loop, fast) >= 0) {
    round++;
    slow = after(n, loop, slow);
    yield snap(12, `Round ${round}: slow moves 1 step, to ${name(slow)}.`);
    fast = after(n, loop, after(n, loop, fast));
    yield snap(13, fast === slow ? `fast moves 2 steps, to ${name(fast)}: the same node as slow.` : `fast moves 2 steps, to ${name(fast)}.`);
    if (slow === fast) {
      yield snap(15, `They meet on ${vals[slow]}: the list loops. Return true.`);
      return true;
    }
  }
  yield snap(11, fast < 0 ? "fast is none: it ran off the end." : `fast is on ${vals[fast]}, the last node: it can't take 2 steps.`);
  yield snap(16, `No loop: return false. slow stands on ${vals[slow]}, the middle node.`);
  return false;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const vals = input.nums as number[];
  const loop = input.loop as number;
  const n = vals.length;
  const v = listOf(s, "list");
  if (!v || s.views.length !== 1) return "needs exactly the list view";
  // The list itself never changes: node i points at i + 1, and the last one at the loop (or none).
  for (const [i, nd] of v.nodes.entries()) {
    const want = i < n - 1 ? `n${i + 1}` : loop >= 0 ? `n${loop}` : null;
    if (nd.id !== `n${i}` || nd.v !== vals[i] || nd.next !== want) return `node ${i} is not the input's node`;
  }
  // Walk k steps from the head by hand.
  const walk = (k: number) => {
    let at = 0;
    for (let t = 0; t < k && at >= 0; t++) at = at + 1 < n ? at + 1 : loop;
    return at;
  };
  const pos = (id: string) => {
    const p = v.pointers.find((q) => q.id === id);
    return p === undefined ? undefined : p.at === null ? -1 : Number(p.at.slice(1));
  };
  const slow = pos("slow"), fast = pos("fast");
  const round = varOf(s, "round") as number;
  if (slow === undefined || fast === undefined || v.pointers.length !== 2) return "needs exactly the pointers slow and fast";
  // After r rounds slow has walked r nodes and fast 2r; on the "slow moves" step fast is one round behind.
  if (slow !== walk(round)) return `slow should be ${round} nodes from the head`;
  if (fast !== walk(s.line === 12 ? 2 * round - 2 : 2 * round)) return `fast should be twice as far as slow`;
  for (const [i, nd] of v.nodes.entries()) {
    const want = i === slow ? "gold" : i === fast ? "steel" : "plain";
    if (nd.state !== want) return `node ${i} is ${nd.state}`;
  }
  if (s.line === 15 && slow !== fast) return "'return true' when slow and fast are apart";
  if (s.line === 11 && !(fast < 0 || walk(2 * round + 1) < 0)) return "the loop may only stop when fast can't take 2 steps";
  if (isLast !== (s.line === 15 || s.line === 16)) return "the trace must end on a return line";
  if (prev && varOf(prev, "round") !== round && varOf(prev, "round") !== round - 1) return "rounds go up one at a time";
  return sayOk(input, s, prev, [1, 2]);
}

export const fastSlowPointers: Pattern = {
  id: "fast-slow-pointers",
  title: "Fast and slow pointers",
  blurb: "One pointer moves 1 node, the other 2: they meet in a loop, or slow ends in the middle.",
  problem: "Does the list loop? The last node links back to the index you give (-1: no loop).",
  section: "Linked list",
  tier: "paid",
  pseudocode,
  fields: [
    { name: "nums", label: "Node values", kind: "ints", min: -99, max: 99, minLen: 1, maxLen: 8 },
    { name: "loop", label: "Last node links to", kind: "int", min: -1, max: 7 },
  ],
  example: { nums: [1, 2, 3, 4, 5, 6], loop: 2 },
  validate(input) {
    const n = (input.nums as number[]).length;
    const loop = input.loop as number;
    return loop >= n ? `With ${n} nodes, the last can link to index 0 to ${n - 1}, or -1 for no loop.` : null;
  },
  random(rng) {
    const n = pick(rng, 4, 8);
    return { nums: list(rng, n, 1, 20), loop: rng() < 0.5 ? -1 : pick(rng, 0, n - 1) };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => (a ? "The list loops: true" : "No loop: false"),
};
