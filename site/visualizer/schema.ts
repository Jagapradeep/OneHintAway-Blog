// One Hint Away step schema, version 1.
// The same JSON is produced by the TypeScript patterns in ./patterns (for the
// website player) and by viz_steps() in post-kit/viz/<pattern>/ref.py (for the
// video). Every step is a full state, never a delta: any step can be drawn on
// its own, and motion comes from comparing two neighbouring steps by id.
//
// This file must stay free of DOM and React, and use only syntax Node can run
// by stripping types (no enums, no parameter properties): the build check
// imports it directly.

export const SCHEMA_VERSION = 1;

/** gold = the current focus, steel = done or compared, dim = out of play,
 *  ghost = a gap between groups, dash = an empty slot (v must be ""). */
export type CellState = "plain" | "gold" | "steel" | "dim" | "ghost" | "dash";
export const CELL_STATES: readonly string[] = ["plain", "gold", "steel", "dim", "ghost", "dash"];

export interface Cell {
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
  /** The cell index this item came from, if any. */
  from?: number;
}

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
  cells: Cell[];
  pointers: Pointer[];
  window?: Win;
  /** Bottom of the stack first. */
  stack?: StackItem[];
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

/** Rules every step of every pattern must obey. Returns the broken rule, or null. */
export function checkStep(trace: Trace, i: number): string | null {
  const s = trace.steps[i];
  const n = trace.steps[0].cells.length;
  if (!Number.isInteger(s.line) || s.line < 0 || s.line >= trace.pseudocode.length) return `line ${s.line} is not a pseudocode line`;
  if (typeof s.say !== "string" || s.say.trim().length < 3) return "narration is empty";
  if (s.say.length > 110) return `narration is ${s.say.length} characters (limit 110)`;
  if (/\s\s|^\s|\s$/.test(s.say)) return "narration has stray spaces";
  if (!Array.isArray(s.cells) || s.cells.length !== n) return `cell count changed from ${n} to ${s.cells?.length}`;
  for (const [k, c] of s.cells.entries()) {
    if (!CELL_STATES.includes(c.state)) return `cell ${k} has unknown state "${c.state}"`;
    if (!isVal(c.v)) return `cell ${k} has no value`;
    if ((c.state === "dash") !== (c.v === "")) return `cell ${k}: "dash" and an empty value must go together`;
  }
  const ids = new Set<string>();
  for (const p of s.pointers) {
    if (!p.id || !p.label) return "a pointer has no id or label";
    if (ids.has(p.id)) return `pointer id "${p.id}" appears twice`;
    ids.add(p.id);
    if (!Number.isInteger(p.at) || p.at < 0 || p.at >= n) return `pointer "${p.id}" is at ${p.at}, outside 0..${n - 1}`;
  }
  if (s.window) {
    const { lo, hi } = s.window;
    if (!Number.isInteger(lo) || !Number.isInteger(hi)) return "window bounds are not whole numbers";
    if (lo < 0 || hi >= n || lo > hi + 1) return `window ${lo}..${hi} is not inside 0..${n - 1}`;
  }
  if (s.stack) {
    const sid = new Set<string>();
    for (const it of s.stack) {
      if (!it.id || sid.has(it.id)) return `stack item id "${it.id}" is missing or repeated`;
      sid.add(it.id);
      if (!isVal(it.v)) return `stack item "${it.id}" has no value`;
      if (it.from !== undefined && (!Number.isInteger(it.from) || it.from < 0 || it.from >= n)) return `stack item "${it.id}" points at cell ${it.from}`;
    }
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

export function pointerAt(step: Step, id: string): number | undefined {
  return step.pointers.find((p) => p.id === id)?.at;
}
