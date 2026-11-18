// Reverse a linked list in place: save the rest, turn the arrow back, move on (post 41).
// The Python twin (post-kit/viz/reverse-list/ref.py) makes the same steps.
import type { Answer, Input, ListNode, ListPointer, Pattern, Step } from "../schema.ts";
import { listOf } from "../schema.ts";
import { list, pick, sayOk, spaced, step } from "./_lib.ts";

const pseudocode = [
  "function reverseList(head):",
  "    prev = none",
  "    curr = head",
  "    while curr != none:",
  "        rest = curr.next   // save it",
  "        curr.next = prev   // turn the arrow",
  "        prev = curr",
  "        curr = rest",
  "    return prev",
];

const LABEL = "Linked list";

function* run(input: Input): Generator<Step, Answer, void> {
  const vals = input.nums as number[];
  const n = vals.length;
  const next: (number | null)[] = vals.map((_, i) => (i + 1 < n ? i + 1 : null));
  const name = (i: number) => (i < 0 || i >= n ? "none" : String(vals[i]));
  const id = (i: number) => (i < 0 || i >= n ? null : `n${i}`);
  let prev = -1, curr = 0, rest: number | null = null;
  const snap = (line: number, say: string) => {
    const nodes: ListNode[] = vals.map((v, i) => ({ id: `n${i}`, v, next: next[i] === null ? null : `n${next[i]}`, state: i === curr ? "gold" : i < curr || i <= prev ? "steel" : "plain" }));
    const pointers: ListPointer[] = [
      { id: "prev", label: "prev", at: id(prev) },
      { id: "curr", label: "curr", at: id(curr) },
    ];
    if (rest !== null) pointers.push({ id: "rest", label: "rest", at: id(rest) });
    return step(line, say, [{ kind: "list", id: "list", label: LABEL, nodes, pointers }]);
  };

  yield snap(2, `prev starts as none, and curr on the head, ${vals[0]}.`);
  while (curr < n) {
    rest = curr + 1;
    yield snap(4, `Save the rest of the list: rest = ${name(rest)}.`);
    next[curr] = prev < 0 ? null : prev;
    yield snap(5, `Turn ${vals[curr]}'s arrow back: it now points to ${name(prev)}.`);
    prev = curr;
    yield snap(6, `prev = curr: the turned part now starts at ${vals[prev]}.`);
    curr = rest;
    yield snap(7, `curr = rest: move on to ${name(curr)}.`);
  }
  yield snap(3, "curr is none, so the loop stops.");
  const out = [...vals].reverse();
  yield snap(8, `Return prev, ${vals[prev]}: the list now reads ${spaced(out)}.`);
  return out;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const vals = input.nums as number[];
  const n = vals.length;
  const v = listOf(s, "list");
  if (!v || s.views.length !== 1) return "needs exactly the list view";
  if (v.nodes.some((nd, i) => nd.id !== `n${i}` || nd.v !== vals[i])) return "the nodes must be the input, in order";
  // Every arrow points forward (not turned yet) or back (turned), and the turned ones come first.
  const fwd = (i: number) => (i + 1 < n ? `n${i + 1}` : null);
  const back = (i: number) => (i > 0 ? `n${i - 1}` : null);
  // (With one node both directions are "none", so only the pointers can be checked.)
  let turned = 0;
  if (n > 1) {
    while (turned < n && v.nodes[turned].next === back(turned)) turned++;
    for (let i = turned; i < n; i++) if (v.nodes[i].next !== fwd(i)) return `node ${i}'s arrow points neither forward nor back in order`;
  }
  const at = (pid: string) => {
    const p = v.pointers.find((q) => q.id === pid);
    return p === undefined ? undefined : p.at === null ? -1 : Number(p.at.slice(1));
  };
  const pv = at("prev"), cu = at("curr"), re = at("rest");
  if (pv === undefined || cu === undefined) return "prev and curr are always shown";
  const c = cu === -1 ? n : cu;
  // prev trails curr by one node, except right after "prev = curr".
  if (s.line === 6 ? pv !== c : pv !== c - 1) return `prev is on ${pv}, curr on ${cu}`;
  if (re !== undefined && s.line >= 4 && s.line <= 6 && (re === -1 ? n : re) !== c + 1) return "rest must be the node after curr";
  if (n > 1 && (s.line === 5 || s.line === 6) && turned !== c + 1) return "after turning, every node up to curr points back";
  if (n > 1 && (s.line === 4 || s.line === 7 || s.line === 2 || s.line === 3 || s.line === 8) && turned !== c) return "only the nodes before curr may point back";
  for (const [i, nd] of v.nodes.entries()) {
    const want = i === c ? "gold" : i < c || i <= pv ? "steel" : "plain";
    if (nd.state !== want) return `node ${i} is ${nd.state}`;
  }
  if (isLast !== (s.line === 8) || (s.line === 8 && (cu !== -1 || pv !== n - 1))) return "the trace ends on 'return prev' with curr on none";
  return sayOk(input, s, prev);
}

export const reverseList: Pattern = {
  id: "reverse-list",
  title: "Reverse a linked list",
  blurb: "Three pointers turn every arrow around in one pass, with no new list.",
  problem: "Reverse the list in place and return its new head.",
  section: "Linked list",
  tier: "free",
  pseudocode,
  fields: [{ name: "nums", label: "Node values", kind: "ints", min: -99, max: 99, minLen: 1, maxLen: 7 }],
  example: { nums: [1, 2, 3, 4, 5] },
  validate: () => null,
  random: (rng) => ({ nums: list(rng, pick(rng, 3, 6), 1, 20) }),
  run,
  check,
  sameAnswer: (_i, got, expected) => JSON.stringify(got) === JSON.stringify(expected),
  answerText: (a) => `Reversed: ${spaced(a as number[])}`,
};
