// One Hint Away step schema, version 2: a step is a list of typed views.
// Each view kind (array, stack, tree; later grid, …) has its own shape, its own
// stable ids, its own generic check below and its own drawing component.
// The same JSON is produced by the TypeScript patterns in ./patterns (for the
// website player) and by viz_steps() in post-kit/viz/<pattern>/ref.py (for the
// video). Every step is a full state, never a delta: any step can be drawn on
// its own, and motion comes from comparing two neighbouring steps by id.
//
// This file must stay free of DOM and React, and use only syntax Node can run
// by stripping types (no enums, no parameter properties): the build check
// imports it directly.

export const SCHEMA_VERSION = 2;

/** gold = the current focus, steel = done or compared, dim = out of play,
 *  ghost = a gap between groups, dash = an empty slot (v must be ""). */
export type CellState = "plain" | "gold" | "steel" | "dim" | "ghost" | "dash";
export const CELL_STATES: readonly string[] = ["plain", "gold", "steel", "dim", "ghost", "dash"];

export interface Cell {
  /** Stable across steps and unique in its view: the cell keeps its id when
   *  it changes position, so a swap can slide. */
  id: string;
  v: number | string;
  state: CellState;
}

export interface Pointer {
  /** Stable across steps, so the player can slide it. */
  id: string;
  label: string;
  /** Cell index. */
  at: number;
}

/** A window over cells lo..hi, both included. lo == hi + 1 means empty. */
export interface Win {
  lo: number;
  hi: number;
  label?: string;
}

export interface StackItem {
  /** Stable across steps, so pushes and pops can animate. */
  id: string;
  v: number | string;
  /** The array view and cell index this item came from, if any. */
  from?: { view: string; at: number };
}

export interface ArrayView {
  kind: "array";
  /** Stable across steps and unique in the step. */
  id: string;
  label?: string;
  cells: Cell[];
  pointers: Pointer[];
  window?: Win;
}

export interface StackView {
  kind: "stack";
  id: string;
  label?: string;
  /** Bottom of the stack first. */
  items: StackItem[];
}

/** gold = the current focus, steel = already visited, dim = ruled out. */
export type NodeState = "plain" | "gold" | "steel" | "dim";
export const NODE_STATES: readonly string[] = ["plain", "gold", "steel", "dim"];

export interface TreeNode {
  /** Stable across steps and unique in its view. */
  id: string;
  v: number | string;
  state: NodeState;
  /** Id of the parent node. Only the root has none. */
  parent?: string;
  /** Which child of its parent this is. Left children are drawn left of the parent. */
  side?: "left" | "right";
}

/** A rooted tree. The whole tree is present on every step; only states change. */
export interface TreeView {
  kind: "tree";
  id: string;
  label?: string;
  /** Any order, but the same on every step. May be empty. */
  nodes: TreeNode[];
}

export type View = ArrayView | StackView | TreeView;

export interface Var {
  name: string;
  /** "" means not set yet. */
  value: number | string;
}

export interface Step {
  /** Index into the trace's pseudocode (0-based). */
  line: number;
  /** One plain-English sentence for this step. */
  say: string;
  /** The same views, in the same order, on every step of a trace. */
  views: View[];
  vars?: Var[];
}

export type Input = Record<string, number | number[]>;
export type Answer = number | string | boolean | null | number[];

export interface Trace {
  schema: number;
  pattern: string;
  input: Input;
  pseudocode: string[];
  steps: Step[];
  answer: Answer;
}

/** One box in the reader's input form. */
export interface Field {
  name: string;
  label: string;
  kind: "ints" | "int";
  /** Smallest and largest value allowed. */
  min: number;
  max: number;
  /** For "ints": how many numbers are allowed. */
  minLen?: number;
  maxLen?: number;
}

/** Everything the engine needs to know about one pattern. Adding a pattern is
 *  one file exporting one of these, plus one line in registry.ts. */
export interface Pattern {
  id: string;
  title: string;
  /** One line for the /visualize list. */
  blurb: string;
  /** What the algorithm is solving, in one sentence. */
  problem: string;
  /** The roadmap section it belongs to; groups the /visualize gallery. */
  section: string;
  /** free = open to everyone for good. paid = a preview once the paywall is on (see access.ts). */
  tier: "free" | "paid";
  /** Slug of the post that teaches it, when there is one. */
  post?: string;
  pseudocode: string[];
  fields: Field[];
  example: Input;
  /** Rules beyond the field limits (such as "must be sorted"). null = fine. */
  validate(input: Input): string | null;
  /** A small, valid input. rng() returns a number in [0, 1). */
  random(rng: () => number): Input;
  /** The algorithm: yields one step at a time, returns the answer. */
  run(input: Input): Generator<Step, Answer, void>;
  /** Pattern rules one step must obey (window sum, stack order, narration).
   *  Written independently of run(). Returns the broken rule, or null. */
  check(input: Input, step: Step, prev: Step | null, isLast: boolean): string | null;
  /** Whether `got` is as right as the brute force's `expected`. */
  sameAnswer(input: Input, got: Answer, expected: Answer): boolean;
  /** The answer in words, for the player's result line. */
  answerText(answer: Answer): string;
}

const MAX_STEPS = 200_000;

export function traceOf(p: Pattern, input: Input): Trace {
  const steps: Step[] = [];
  const it = p.run(input);
  for (;;) {
    const r = it.next();
    if (r.done) {
      return { schema: SCHEMA_VERSION, pattern: p.id, input, pseudocode: p.pseudocode, steps, answer: r.value };
    }
    steps.push(r.value);
    if (steps.length > MAX_STEPS) throw new Error(`${p.id}: more than ${MAX_STEPS} steps`);
  }
}

/** Field limits only. Returns the problem in words, or null. */
export function checkLimits(fields: Field[], input: Input): string | null {
  for (const f of fields) {
    const v = input[f.name];
    const inRange = (x: unknown) => typeof x === "number" && Number.isInteger(x) && x >= f.min && x <= f.max;
    if (f.kind === "int") {
      if (!inRange(v)) return `${f.label} must be a whole number from ${f.min} to ${f.max}.`;
    } else {
      if (!Array.isArray(v)) return `${f.label} must be a list of numbers.`;
      const lo = f.minLen ?? 0;
      const hi = f.maxLen ?? Infinity;
      if (v.length < lo || v.length > hi) return `${f.label} needs ${lo} to ${hi} numbers.`;
      if (!v.every(inRange)) return `Every number in ${f.label} must be a whole number from ${f.min} to ${f.max}.`;
    }
  }
  return null;
}

const isVal = (v: unknown) => typeof v === "string" || (typeof v === "number" && Number.isFinite(v));

/** Rules every array view must obey. `first` is the same view on step 1. */
function checkArray(v: ArrayView, first: ArrayView): string | null {
  const n = first.cells.length;
  if (!Array.isArray(v.cells) || v.cells.length !== n) return `cell count changed from ${n} to ${v.cells?.length}`;
  const cellIds = new Set<string>();
  for (const [k, c] of v.cells.entries()) {
    if (!c.id || cellIds.has(c.id)) return `cell ${k}: id "${c.id}" is missing or repeated`;
    cellIds.add(c.id);
    if (!CELL_STATES.includes(c.state)) return `cell ${k} has unknown state "${c.state}"`;
    if (!isVal(c.v)) return `cell ${k} has no value`;
    if ((c.state === "dash") !== (c.v === "")) return `cell ${k}: "dash" and an empty value must go together`;
  }
  // Cells may change places, but never appear or disappear.
  for (const c of first.cells) if (!cellIds.has(c.id)) return `cell "${c.id}" disappeared`;
  if (!Array.isArray(v.pointers)) return "no pointer list";
  const ids = new Set<string>();
  for (const p of v.pointers) {
    if (!p.id || !p.label) return "a pointer has no id or label";
    if (ids.has(p.id)) return `pointer id "${p.id}" appears twice`;
    ids.add(p.id);
    if (!Number.isInteger(p.at) || p.at < 0 || p.at >= n) return `pointer "${p.id}" is at ${p.at}, outside 0..${n - 1}`;
  }
  if (v.window) {
    const { lo, hi } = v.window;
    if (!Number.isInteger(lo) || !Number.isInteger(hi)) return "window bounds are not whole numbers";
    if (lo < 0 || hi >= n || lo > hi + 1) return `window ${lo}..${hi} is not inside 0..${n - 1}`;
  }
  return null;
}

/** Rules every stack view must obey. */
function checkStack(v: StackView, step: Step): string | null {
  if (!Array.isArray(v.items)) return "no item list";
  const ids = new Set<string>();
  for (const it of v.items) {
    if (!it.id || ids.has(it.id)) return `item id "${it.id}" is missing or repeated`;
    ids.add(it.id);
    if (!isVal(it.v)) return `item "${it.id}" has no value`;
    if (it.from !== undefined) {
      const src = arrayOf(step, it.from.view);
      if (!src) return `item "${it.id}" comes from "${it.from.view}", which is not an array view`;
      if (!Number.isInteger(it.from.at) || it.from.at < 0 || it.from.at >= src.cells.length) return `item "${it.id}" points at cell ${it.from.at}`;
    }
  }
  return null;
}

/** Rules every tree view must obey. `first` is the same view on step 1. */
function checkTree(v: TreeView, first: TreeView): string | null {
  if (!Array.isArray(v.nodes) || v.nodes.length !== first.nodes.length) return `node count changed from ${first.nodes.length} to ${v.nodes?.length}`;
  const parentOf = new Map<string, string | undefined>();
  const sides = new Set<string>();
  let roots = 0;
  for (const [k, nd] of v.nodes.entries()) {
    const f = first.nodes[k];
    if (!nd.id || parentOf.has(nd.id)) return `node id "${nd.id}" is missing or repeated`;
    if (nd.id !== f.id || nd.parent !== f.parent || nd.side !== f.side) return `node ${k} ("${f.id}") changed its id, parent or side`;
    parentOf.set(nd.id, nd.parent);
    if (!NODE_STATES.includes(nd.state)) return `node "${nd.id}" has unknown state "${nd.state}"`;
    if (!isVal(nd.v)) return `node "${nd.id}" has no value`;
    if (nd.side !== undefined && nd.side !== "left" && nd.side !== "right") return `node "${nd.id}" has side "${nd.side}"`;
    if (nd.parent === undefined) {
      roots++;
      if (nd.side !== undefined) return `the root "${nd.id}" has a side`;
    } else if (nd.side) {
      const key = `${nd.parent} ${nd.side}`;
      if (sides.has(key)) return `node "${nd.parent}" has two ${nd.side} children`;
      sides.add(key);
    }
  }
  if (v.nodes.length > 0 && roots !== 1) return `${roots} roots (a tree has exactly one)`;
  // Every node must reach the root: no missing parents, no cycles.
  const ok = new Set<string>();
  for (const nd of v.nodes) {
    const path: string[] = [];
    let at: string | undefined = nd.id;
    while (at !== undefined && !ok.has(at)) {
      if (!parentOf.has(at)) return `node "${path[path.length - 1]}" has parent "${at}", which is not a node`;
      if (path.includes(at)) return `node "${at}" is its own ancestor`;
      path.push(at);
      at = parentOf.get(at);
    }
    for (const id of path) ok.add(id);
  }
  return null;
}

/** Rules every step of every pattern must obey. Returns the broken rule, or null. */
export function checkStep(trace: Trace, i: number): string | null {
  const s = trace.steps[i];
  const first = trace.steps[0];
  if (!Number.isInteger(s.line) || s.line < 0 || s.line >= trace.pseudocode.length) return `line ${s.line} is not a pseudocode line`;
  if (typeof s.say !== "string" || s.say.trim().length < 3) return "narration is empty";
  if (s.say.length > 110) return `narration is ${s.say.length} characters (limit 110)`;
  if (/\s\s|^\s|\s$/.test(s.say)) return "narration has stray spaces";
  if (!Array.isArray(s.views) || s.views.length === 0) return "a step needs at least one view";
  if (s.views.length !== first.views.length) return `view count changed from ${first.views.length} to ${s.views.length}`;
  const viewIds = new Set<string>();
  for (const [k, v] of s.views.entries()) {
    const f = first.views[k];
    if (!v.id || viewIds.has(v.id)) return `view id "${v.id}" is missing or repeated`;
    viewIds.add(v.id);
    if (v.kind !== f.kind || v.id !== f.id) return `view ${k} changed from ${f.kind} "${f.id}" to ${v.kind} "${v.id}"`;
    let why: string | null;
    if (v.kind === "array") why = checkArray(v, f as ArrayView);
    else if (v.kind === "stack") why = checkStack(v, s);
    else if (v.kind === "tree") why = checkTree(v, f as TreeView);
    else why = "unknown kind of view";
    if (why) return `${(v as View).kind} "${(v as View).id}": ${why}`;
  }
  if (s.vars) {
    const names = new Set<string>();
    for (const v of s.vars) {
      if (!v.name || names.has(v.name)) return `variable "${v.name}" is missing or repeated`;
      names.add(v.name);
      if (!isVal(v.value)) return `variable "${v.name}" has no value`;
    }
  }
  return null;
}

/** Every whole number written in a narration line. */
export function numbersIn(say: string): number[] {
  return (say.match(/-?\d+/g) ?? []).map(Number);
}

/** Narration may only mention numbers that are true of the step. */
export function strayNumber(say: string, facts: Iterable<number>): string | null {
  const ok = new Set(facts);
  for (const x of numbersIn(say)) if (!ok.has(x)) return `narration mentions ${x}, which is not in the step's state`;
  return null;
}

export function varOf(step: Step, name: string): number | string | undefined {
  return step.vars?.find((v) => v.name === name)?.value;
}

/** The step's array view with this id, or its first array view. */
export function arrayOf(step: Step, id?: string): ArrayView | undefined {
  return step.views.find((v): v is ArrayView => v.kind === "array" && (id === undefined || v.id === id));
}

/** The step's stack view with this id, or its first stack view. */
export function stackOf(step: Step, id?: string): StackView | undefined {
  return step.views.find((v): v is StackView => v.kind === "stack" && (id === undefined || v.id === id));
}

/** The step's tree view with this id, or its first tree view. */
export function treeOf(step: Step, id?: string): TreeView | undefined {
  return step.views.find((v): v is TreeView => v.kind === "tree" && (id === undefined || v.id === id));
}

/** Where a pointer of the first array view stands. */
export function pointerAt(step: Step, id: string): number | undefined {
  return arrayOf(step)?.pointers.find((p) => p.id === id)?.at;
}
