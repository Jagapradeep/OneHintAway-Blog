// The backtracking template: choose, explore, undo (post 38). The player walks
// permute, the post's first worked example; the post's pseudocode also holds
// find (combination sum). The tree is every choice the search makes; the path
// from the top to the gold node is the current path.
import type { Answer, ArrayView, Input, Pattern, Step, TreeNode, TreeView } from "../schema.ts";
import { treeOf, varOf } from "../schema.ts";
import { arr, list, pick, sayOk, step, tiles } from "./_lib.ts";

const pseudocode = [
  "function permute(nums, used, path, out):",
  "    if length(path) == length(nums):",
  "        add a copy of path to out",
  "        return out",
  "    for i from 0 to length(nums) - 1:",
  "        if not used[i]:",
  "            used[i] = true   // choose",
  "            add nums[i] to path",
  "            permute(nums, used, path, out)",
  "            remove last from path   // undo",
  "            used[i] = false",
  "    return out",
  "",
  "function find(nums, i, left, path, out):",
  "    if left == 0:",
  "        add a copy of path to out",
  "        return out",
  "    for j from i to length(nums) - 1:",
  "        if nums[j] <= left:",
  "            add nums[j] to path   // choose",
  "            rest = left - nums[j]",
  "            find(nums, j, rest, path, out)",
  "            remove last from path   // undo",
  "    return out",
];

const box = (a: number[]) => (a.length ? a.join(" ") : "[ ]");

/** Every partial order as a node: id "r", then "r.0", "r.0.2", … (cell indexes). */
function treeFor(nums: number[]) {
  const nodes: { id: string; v: string; parent?: string; idx: number[] }[] = [];
  const grow = (id: string, idx: number[], v: string, parent?: string) => {
    nodes.push({ id, v, parent, idx });
    for (let i = 0; i < nums.length; i++) if (!idx.includes(i)) grow(`${id}.${i}`, [...idx, i], String(nums[i]), id);
  };
  grow("r", [], "[ ]");
  return nodes;
}

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const all = treeFor(nums);
  const finished = new Set<string>();
  const used = nums.map(() => false);
  const path: number[] = []; // cell indexes
  const out: string[] = [];
  let at = "r";
  let ptr = -1;
  const t = tiles(nums);
  const snap = (line: number, say: string) => {
    const nodes: TreeNode[] = all.map((nd) => ({
      id: nd.id, v: nd.v, parent: nd.parent,
      state: nd.id === at ? "gold" : at.startsWith(`${nd.id}.`) ? "steel" : finished.has(nd.id) ? "dim" : "plain",
    }));
    return step(line, say, [
      { kind: "tree", id: "tree", nodes } as TreeView,
      arr("nums", t, (i) => (i === ptr ? "gold" : used[i] ? "steel" : "plain"), [], { label: "nums: steel = used" }),
    ], { path: box(path.map((i) => nums[i])), saved: out.length });
  };

  function* permute(): Generator<Step, void, void> {
    if (path.length === nums.length) {
      out.push(box(path.map((i) => nums[i])));
      ptr = -1;
      yield snap(2, `The path is full: save a copy of ${out[out.length - 1]}.`);
      finished.add(at);
      return;
    }
    const here = at;
    for (let i = 0; i < nums.length; i++) {
      ptr = i;
      if (used[i]) {
        yield snap(5, `nums[${i}] = ${nums[i]} is already on the path: skip it.`);
        continue;
      }
      used[i] = true;
      path.push(i);
      at = `${here}.${i}`;
      yield snap(6, `Choose nums[${i}] = ${nums[i]}: mark it used. The path is ${box(path.map((k) => nums[k]))}.`);
      yield* permute();
      at = here;
      path.pop();
      used[i] = false;
      ptr = i;
      yield snap(9, `Undo: take ${nums[i]} off the path and free it.`);
    }
    ptr = -1;
    finished.add(here);
  }

  yield snap(0, "Start with nothing used and an empty path.");
  yield* permute();
  at = "";
  yield snap(11, `Every order is saved: ${out.length} in all.`);
  return out.join(" | ");
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const tv = treeOf(s, "tree");
  const a = s.views[1] as ArrayView;
  const saved = varOf(s, "saved") as number;
  if (!tv || s.views.length !== 2 || a?.id !== "nums") return "needs the tree and nums";
  if (a.cells.some((c, i) => c.v !== nums[i])) return "nums must be the input";
  const byId = new Map(tv.nodes.map((nd) => [nd.id, nd]));
  const gold = tv.nodes.filter((nd) => nd.state === "gold");
  if (gold.length > 1) return "at most one node is the current call";
  const chain: string[] = [];
  for (let id: string | undefined = gold[0]?.id; id !== undefined; id = byId.get(id)?.parent) chain.unshift(id);
  if (tv.nodes.some((nd) => (nd.state === "steel") !== (chain.includes(nd.id) && nd.id !== gold[0]?.id))) return "only the path to the current call is lit";
  // The path is the values on the way down; the used cells are exactly the ones on it.
  const idx = chain.slice(1).map((id) => Number(id.slice(id.lastIndexOf(".") + 1)));
  if (varOf(s, "path") !== (idx.length ? idx.map((i) => nums[i]).join(" ") : "[ ]")) return "path must be the values on the way to the current call";
  const lit = a.cells.flatMap((c, k) => (c.state === "gold" ? [k] : []));
  if (lit.length > 1) return "at most one cell is the one being tried";
  const ptr = lit[0];
  for (const [i, c] of a.cells.entries()) {
    if (c.state === "steel" && !idx.includes(i)) return `cell ${i} is lit but not on the path`;
    if (c.state === "plain" && idx.includes(i)) return `cell ${i} is on the path but not lit`;
  }
  if (s.line === 5 && (ptr === undefined || !idx.includes(ptr))) return "'skip' only for a used value";
  if (s.line === 6 && idx[idx.length - 1] !== ptr) return "the chosen value ends the path";
  if (s.line === 2 && idx.length !== nums.length) return "a copy is saved only when the path is full";
  const leaves = tv.nodes.filter((nd) => nd.id.split(".").length === nums.length + 1 && nd.state === "dim").length + (s.line === 2 ? 1 : 0);
  if (saved !== leaves) return `${saved} orders saved, ${leaves} done`;
  let fact = 1;
  for (let k = 2; k <= nums.length; k++) fact *= k;
  if (isLast !== (s.line === 11) || (isLast && saved !== fact)) return `the trace ends after all ${fact} orders`;
  return sayOk(input, s, prev);
}

export const permutations: Pattern = {
  id: "permutations",
  title: "Backtracking template",
  blurb: "Choose, explore, undo, try the next: every order of the numbers, one path at a time.",
  problem: "List every order of the numbers.",
  section: "Backtracking",
  tier: "paid",
  pseudocode,
  fields: [{ name: "nums", label: "Numbers", kind: "ints", min: 0, max: 9, minLen: 1, maxLen: 3 }],
  example: { nums: [1, 2, 3] },
  validate: () => null,
  random: (rng) => ({ nums: list(rng, pick(rng, 2, 3), 1, 9) }),
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => `${String(a).split("|").length} orders: ${a}`,
};
