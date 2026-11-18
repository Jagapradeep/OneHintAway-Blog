// Subsets: for each value, pick it and decide the rest, then undo the pick and
// decide the rest again (post 37). The tree is every choice the search makes;
// the path from the top to the gold node is the current list of picks.
import type { Answer, Input, MapView, Pattern, Step, TreeNode, TreeView } from "../schema.ts";
import { treeOf, varOf } from "../schema.ts";
import { list, pick, sayOk, step } from "./_lib.ts";

const pseudocode = [
  "function build(nums, i, picked, out):",
  "    if i == length(nums):",
  "        add a copy of picked to out",
  "    else:",
  "        add nums[i] to picked   // pick",
  "        build(nums, i + 1, picked, out)",
  "        remove last from picked   // skip",
  "        build(nums, i + 1, picked, out)",
  "function subsets(nums):",
  "    out = empty list",
  "    build(nums, 0, empty list, out)",
  "    return out",
];

const box = (a: number[]) => (a.length ? `[${a.join(" ")}]` : "[ ]");

/** The whole decision tree: node "r", its pick child "rp", its skip child "rs", … */
function treeFor(nums: number[]) {
  const nodes: { id: string; v: string; parent?: string; depth: number }[] = [];
  const grow = (id: string, depth: number, v: string, parent?: string) => {
    nodes.push({ id, v, parent, depth });
    if (depth === nums.length) return;
    grow(`${id}p`, depth + 1, `+${nums[depth]}`, id);
    grow(`${id}s`, depth + 1, `no ${nums[depth]}`, id);
  };
  grow("r", 0, "[ ]");
  return nodes;
}

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const all = treeFor(nums);
  const finished = new Set<string>();
  let at = "r";
  const picked: number[] = [];
  const out: number[][] = [];
  const snap = (line: number, say: string) => {
    const nodes: TreeNode[] = all.map((nd) => ({
      id: nd.id, v: nd.v, parent: nd.parent,
      state: nd.id === at ? "gold" : at.startsWith(nd.id) ? "steel" : finished.has(nd.id) ? "dim" : "plain",
    }));
    const saved: MapView = { kind: "map", id: "out", label: "out", entries: out.map((s, k) => ({ id: `o${k}`, k: k + 1, v: box(s), state: k === out.length - 1 && line === 2 ? "gold" : "plain" })) };
    return step(line, say, [{ kind: "tree", id: "tree", label: "Every choice: +x picks x, no x skips it", nodes } as TreeView, saved], { i: at ? at.length - 1 : "", picked: box(picked) });
  };

  function* build(i: number): Generator<Step, void, void> {
    if (i === nums.length) {
      out.push([...picked]);
      yield snap(2, `All ${nums.length} values decided: save a copy of ${box(picked)}.`);
      finished.add(at);
      return;
    }
    const here = at;
    picked.push(nums[i]);
    at = `${here}p`;
    yield snap(4, `Pick ${nums[i]}: picked is now ${box(picked)}.`);
    yield* build(i + 1);
    at = here;
    picked.pop();
    yield snap(6, `Back at ${nums[i]}: remove it, so picked is ${box(picked)} again.`);
    at = `${here}s`;
    yield snap(7, `Now skip ${nums[i]} and decide the rest.`);
    yield* build(i + 1);
    at = here;
    finished.add(here);
  }

  yield snap(10, "Start with nothing picked, then decide each value in turn.");
  yield* build(0);
  at = "";
  yield snap(11, `Every value was decided both ways: ${out.length} subsets.`);
  return out.map(box).join(" ");
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const t = treeOf(s, "tree");
  const out = s.views[1] as MapView;
  if (!t || s.views.length !== 2 || out?.kind !== "map") return "needs the tree and the out list";
  if (t.nodes.length !== 2 ** (nums.length + 1) - 1) return "the tree must hold every choice";
  const byId = new Map(t.nodes.map((nd) => [nd.id, nd]));
  const gold = t.nodes.filter((nd) => nd.state === "gold");
  if (gold.length > 1) return "at most one node is the current call";
  // The steel nodes are exactly the ancestors of the current call.
  const path: string[] = [];
  for (let id = gold[0]?.parent; id !== undefined; id = byId.get(id)?.parent) path.push(id);
  if (t.nodes.some((nd) => (nd.state === "steel") !== path.includes(nd.id))) return "only the path to the current call is lit";
  // picked holds the values picked along that path.
  const chain = gold[0] ? [...path.reverse(), gold[0].id] : [];
  const want = chain.slice(1).flatMap((id) => (id.endsWith("p") ? [nums[id.length - 2]] : []));
  const shown = String(varOf(s, "picked"));
  if (shown !== `[${want.length ? want.join(" ") : " "}]`) return `picked shows ${shown}, the path picks ${want.join(" ")}`;
  // Every saved subset is a leaf the search has reached.
  const leaves = t.nodes.filter((nd) => nd.id.length === nums.length + 1 && nd.state === "dim").length + (s.line === 2 ? 1 : 0);
  if (out.entries.length !== leaves) return `${out.entries.length} subsets saved, ${leaves} leaves done`;
  if (s.line === 2 && gold[0]?.id.length !== nums.length + 1) return "a copy is saved only at a leaf";
  if (isLast !== (s.line === 11) || (isLast && out.entries.length !== 2 ** nums.length)) return `the trace ends after all ${2 ** nums.length} subsets`;
  return sayOk(input, s, prev, [nums.length, out.entries.length]);
}

export const subsets: Pattern = {
  id: "subsets",
  title: "Subsets",
  blurb: "Pick, explore, undo, skip: backtracking lists every group you could choose.",
  problem: "List every subset of the numbers, the empty one too.",
  section: "Backtracking",
  tier: "free",
  pseudocode,
  fields: [{ name: "nums", label: "Numbers", kind: "ints", min: 0, max: 9, minLen: 1, maxLen: 3 }],
  example: { nums: [1, 2, 3] },
  validate: () => null,
  random: (rng) => ({ nums: list(rng, pick(rng, 2, 3), 1, 9) }),
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => `${String(a).split("]").length - 1} subsets: ${a}`,
};
