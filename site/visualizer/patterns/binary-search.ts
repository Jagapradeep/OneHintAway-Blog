// Binary search on a sorted array (LeetCode 704), shown twice: the array with
// the live range framed, and the decision tree of every middle the search can
// check, with the path taken lit. Node m<i> is the check of cell i, so it sits
// in that cell's column. Mirrors post-kit/viz/binary-search/ref.py step for step.
import type { Answer, Cell, Input, NodeState, Pattern, Step, TreeNode } from "../schema.ts";
import { arrayOf, strayNumber, treeOf, varOf } from "../schema.ts";

const pseudocode = [
  "function search(nums, target):",
  "    low = 0",
  "    high = length(nums) - 1",
  "    while low <= high:",
  "        middle = floor((low + high) / 2)",
  "        if nums[middle] == target:",
  "            return middle",
  "        else if nums[middle] < target:",
  "            low = middle + 1",
  "        else:",
  "            high = middle - 1",
  "    return -1",
];

const L_START = 2, L_MID = 4, L_FOUND = 6, L_LOW = 8, L_HIGH = 10, L_NONE = 11;
const TREE_LABEL = "Every middle the search can check";

function* run(input: Input): Generator<Step, Answer, void> {
  const nums = input.nums as number[];
  const target = input.target as number;
  let low = 0;
  let high = nums.length - 1;
  let middle: number | "" = "";
  const tried: number[] = [];

  const snap = (line: number, say: string): Step => {
    const focus = line === L_MID || line === L_FOUND;
    const out = (i: number) => i < low || i > high || line === L_FOUND;
    const nodes: TreeNode[] = [];
    // Pre-order: a node, then everything left of it, then everything right.
    const grow = (lo: number, hi: number, parent?: string, side?: "left" | "right") => {
      if (lo > hi) return;
      const m = lo + Math.floor((hi - lo) / 2);
      const state: NodeState = focus && m === middle ? "gold" : tried.includes(m) ? "steel" : out(m) ? "dim" : "plain";
      nodes.push(parent === undefined ? { id: `m${m}`, v: nums[m], state } : { id: `m${m}`, v: nums[m], state, parent, side });
      grow(lo, m - 1, `m${m}`, "left");
      grow(m + 1, hi, `m${m}`, "right");
    };
    grow(0, nums.length - 1);
    return {
      line,
      say,
      views: [
        {
          kind: "array",
          id: "nums",
          cells: nums.map((v, i): Cell => ({ id: `c${i}`, v, state: focus && i === middle ? "gold" : out(i) ? "dim" : "plain" })),
          pointers: middle === "" ? [] : [{ id: "middle", label: "middle", at: middle }],
          window: { lo: low, hi: high },
        },
        { kind: "tree", id: "tree", label: TREE_LABEL, nodes },
      ],
      vars: [
        { name: "target", value: target },
        { name: "low", value: low },
        { name: "high", value: high },
        { name: "middle", value: middle },
      ],
    };
  };

  if (nums.length === 0) {
    yield snap(L_NONE, `There are no numbers, so ${target} is not here.`);
    return -1;
  }
  yield snap(L_START, `Look for ${target}. It can be anywhere from index ${low} to index ${high}.`);
  while (low <= high) {
    middle = low + Math.floor((high - low) / 2);
    tried.push(middle);
    const v = nums[middle];
    yield snap(L_MID, `The middle of index ${low} to ${high} is index ${middle}. It holds ${v}.`);
    if (v === target) {
      yield snap(L_FOUND, `${v} is the target. Found it at index ${middle}.`);
      return middle;
    } else if (v < target) {
      low = middle + 1;
      yield snap(L_LOW, `${v} is less than ${target}: too small, so the left half goes. low = ${low}.`);
    } else {
      high = middle - 1;
      yield snap(L_HIGH, `${v} is more than ${target}: too big, so the right half goes. high = ${high}.`);
    }
  }
  yield snap(L_NONE, `low has passed high: nothing is left to check, so ${target} is not here.`);
  return -1;
}

/** The decision tree, worked out without recursion: node index -> [parent index, side]. */
function shapeOf(n: number): Map<number, [number, string] | null> {
  const want = new Map<number, [number, string] | null>();
  const todo: [number, number, [number, string] | null][] = [[0, n - 1, null]];
  while (todo.length) {
    const [lo, hi, up] = todo.pop()!;
    if (lo > hi) continue;
    const m = (lo + hi) >> 1;
    want.set(m, up);
    todo.push([lo, m - 1, [m, "left"]], [m + 1, hi, [m, "right"]]);
  }
  return want;
}

const lit = (step: Step) => new Set(treeOf(step)!.nodes.filter((nd) => nd.state === "gold" || nd.state === "steel").map((nd) => nd.id));

function check(input: Input, step: Step, prev: Step | null, isLast: boolean): string | null {
  const nums = input.nums as number[];
  const target = input.target as number;
  const n = nums.length;
  const arr = arrayOf(step, "nums");
  const tree = treeOf(step, "tree");
  if (!arr || !tree || step.views.length !== 2) return "needs exactly the array view nums and the tree view tree";
  if (varOf(step, "target") !== target) return "target changed";
  const low = varOf(step, "low") as number;
  const high = varOf(step, "high") as number;
  const middle = varOf(step, "middle") as number | "";
  if (!Number.isInteger(low) || !Number.isInteger(high)) return "low and high must be whole numbers";
  if (middle !== "" && (!Number.isInteger(middle) || middle < 0 || middle >= n)) return `middle ${middle} is not a cell`;
  if (!arr.window || arr.window.lo !== low || arr.window.hi !== high) return `the window must frame low..high (${low}..${high})`;
  const wantPtr = middle === "" ? "" : `middle@${middle}`;
  if (arr.pointers.map((q) => `${q.id}@${q.at}`).join() !== wantPtr) return "the only pointer is middle, once there is one";

  const found = step.line === L_FOUND;
  const focus = found || step.line === L_MID;
  for (const [i, c] of arr.cells.entries()) {
    if (c.id !== `c${i}`) return `cell ${i} has id ${c.id}: cells never move here`;
    if (c.v !== nums[i]) return `cell ${i} shows ${c.v}, the input has ${nums[i]}`;
    const want = focus && i === middle ? "gold" : i < low || i > high || found ? "dim" : "plain";
    if (c.state !== want) return `cell ${i} is ${c.state}, expected ${want}`;
  }

  // The tree is the decision tree of this array: one node per cell.
  const shape = shapeOf(n);
  if (tree.nodes.length !== n) return `the tree has ${tree.nodes.length} nodes for ${n} cells`;
  const before = prev ? lit(prev) : new Set<string>();
  const now = lit(step);
  for (const nd of tree.nodes) {
    const i = Number(nd.id.slice(1));
    if (nd.id !== `m${i}` || !shape.has(i)) return `node "${nd.id}" is not the check of a cell`;
    if (nd.v !== nums[i]) return `node ${nd.id} shows ${nd.v}, cell ${i} holds ${nums[i]}`;
    const up = shape.get(i)!;
    if (up === null ? nd.parent !== undefined : nd.parent !== `m${up[0]}` || nd.side !== up[1]) return `node ${nd.id} hangs in the wrong place`;
    const isLit = before.has(nd.id) || (step.line === L_MID && i === middle);
    if (now.has(nd.id) !== isLit) return `node ${nd.id}: the lit path must be the middles checked so far`;
    const want = focus && i === middle ? "gold" : isLit ? "steel" : i < low || i > high || found ? "dim" : "plain";
    if (nd.state !== want) return `node ${nd.id} is ${nd.state}, expected ${want}`;
  }

  const same = (name: string) => prev !== null && varOf(prev, name) === varOf(step, name);
  const after = (...lines: number[]) => prev !== null && lines.includes(prev.line);
  switch (step.line) {
    case L_START:
      if (prev || n === 0 || low !== 0 || high !== n - 1 || middle !== "") return "the first step must set low and high to the two ends";
      break;
    case L_MID:
      if (!after(L_START, L_LOW, L_HIGH) || !same("low") || !same("high") || low > high) return "a middle is picked only while low <= high, without moving them";
      if (middle !== low + Math.floor((high - low) / 2)) return `middle ${middle} is not the middle of ${low}..${high}`;
      break;
    case L_FOUND:
      if (!after(L_MID) || !same("low") || !same("high") || !same("middle") || middle === "" || nums[middle] !== target) return "'found' without the target in the middle";
      if (!isLast) return "steps continue after the answer";
      break;
    case L_LOW:
      if (!after(L_MID) || !same("high") || !same("middle") || middle === "" || nums[middle] >= target || low !== middle + 1) return "low may only move to middle + 1, when the middle is too small";
      break;
    case L_HIGH:
      if (!after(L_MID) || !same("low") || !same("middle") || middle === "" || nums[middle] <= target || high !== middle - 1) return "high may only move to middle - 1, when the middle is too big";
      break;
    case L_NONE:
      if (!isLast || low <= high) return "'return -1' while there is still a range to check";
      if (n === 0 ? prev !== null : !after(L_LOW, L_HIGH) || !same("low") || !same("high") || !same("middle")) return "'return -1' must follow the move that emptied the range";
      break;
    default:
      return `line ${step.line} never gets a step`;
  }
  if (isLast && step.line !== L_FOUND && step.line !== L_NONE) return "the trace stops without an answer";
  const facts = [target, low, high];
  if (middle !== "") facts.push(middle, nums[middle]);
  return strayNumber(step.say, facts);
}

function random(rng: () => number): Input {
  const n = 6 + Math.floor(rng() * 5);
  const nums: number[] = [];
  let v = Math.floor(rng() * 5);
  for (let i = 0; i < n; i++) {
    v += 2 + Math.floor(rng() * 4); // gaps of at least 2, so "one more" is never in the array
    nums.push(v);
  }
  const pick = nums[Math.floor(rng() * n)];
  return { nums, target: rng() < 0.75 ? pick : pick + 1 };
}

export const binarySearch: Pattern = {
  id: "binary-search",
  title: "Binary search",
  blurb: "A sorted array and one value to find: check the middle, drop the half that can't hold it.",
  problem: "Find the target's index in a sorted array, or -1 when it is not there.",
  section: "Binary search",
  tier: "free",
  post: "binary-search",
  pseudocode,
  fields: [
    { name: "nums", label: "Sorted numbers", kind: "ints", min: -99, max: 99, minLen: 1, maxLen: 10 },
    { name: "target", label: "Target", kind: "int", min: -99, max: 99 },
  ],
  example: { nums: [1, 3, 5, 7, 9, 11], target: 7 },
  validate(input) {
    const nums = input.nums as number[];
    for (let i = 1; i < nums.length; i++) {
      if (nums[i] < nums[i - 1]) return `The numbers must be sorted from small to large: ${nums[i]} comes after ${nums[i - 1]}.`;
    }
    return null;
  },
  random,
  run,
  check,
  // With repeated numbers, any index that holds the target is right.
  sameAnswer: (input, got, expected) =>
    expected === -1 ? got === -1 : typeof got === "number" && (input.nums as number[])[got] === input.target,
  answerText: (a) => (a === -1 ? "Not in the array: return -1" : `Found at index ${a}`),
};
