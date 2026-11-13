// Building blocks shared by the pattern files: views, steps, and the checks
// most patterns need. No DOM, no React (the build check imports this in Node).
import type { ArrayView, CellState, Input, Pointer, Step, View, Win } from "../schema.ts";
import { strayNumber } from "../schema.ts";

/** A value with a stable id, so its cell can slide when it changes position. */
export interface Tile {
  id: string;
  v: number | string;
}
export const tiles = (vals: (number | string)[]): Tile[] => vals.map((v, i) => ({ id: `c${i}`, v }));

/** Pointers named after their variable. One that stands outside the cells is left out. */
export const ptrs = (n: number, at: Record<string, number>): Pointer[] =>
  Object.entries(at)
    .filter(([, i]) => i >= 0 && i < n)
    .map(([id, i]) => ({ id, label: id, at: i }));

/** An array view. An empty value ("") is drawn as an empty slot. */
export function arr(
  id: string,
  t: Tile[],
  state: (i: number) => CellState,
  pointers: Pointer[] = [],
  more: { window?: Win; label?: string; hideIndex?: boolean } = {},
): ArrayView {
  return { kind: "array", id, ...more, cells: t.map((x, i) => ({ id: x.id, v: x.v, state: x.v === "" ? "dash" : state(i) })), pointers };
}

export const step = (line: number, say: string, views: View[], v: Record<string, number | string> = {}): Step => ({
  line,
  say,
  views,
  vars: Object.entries(v).map(([name, value]) => ({ name, value })),
});

export const swap = <T>(a: T[], i: number, j: number) => {
  [a[i], a[j]] = [a[j], a[i]];
};
export const sum = (a: number[]) => a.reduce((x, y) => x + y, 0);
export const ascending = (a: number[]) => a.every((x, i) => i === 0 || a[i - 1] <= x);
export const sortedCopy = (a: number[]) => [...a].sort((x, y) => x - y);
export const eq = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);

/** The numbers an array view shows, left to right. */
export const vals = (s: Step, id: string): number[] =>
  (s.views.find((v) => v.kind === "array" && v.id === id) as ArrayView).cells.map((c) => c.v as number);

/** Every number a step shows, plus every number of the input. */
function facts(input: Input, s: Step): number[] {
  const out: number[] = [];
  const add = (x: unknown) => {
    if (typeof x === "number") out.push(x);
    else if (Array.isArray(x)) x.forEach(add);
  };
  add(Object.values(input));
  s.vars?.forEach((v) => add(v.value));
  for (const v of s.views) {
    if (v.kind === "array") add([v.cells.length, v.cells.map((c, i) => [c.v, i]), v.pointers.map((p) => p.at), v.window ? [v.window.lo, v.window.hi] : []]);
    else if (v.kind === "stack") add(v.items.map((i) => i.v));
    else if (v.kind === "tree") add(v.nodes.map((n) => n.v));
    else if (v.kind === "map") add(v.entries.map((e) => [e.k, e.v]));
    else if (v.kind === "bars") add(v.bars.map((b, i) => [b.h, b.water, i]));
    else if (v.kind === "grid") add(v.rows.map((r, y) => r.map((c, x) => [c.v, x, y])));
  }
  return out;
}

/** Narration may only mention numbers shown on this step or the one before, or given in `extra`. */
export const sayOk = (input: Input, s: Step, prev: Step | null, extra: number[] = []) =>
  strayNumber(s.say, [...facts(input, s), ...(prev ? facts(input, prev) : []), ...extra]);

/** A whole number from lo to hi. */
export const pick = (rng: () => number, lo: number, hi: number) => lo + Math.floor(rng() * (hi - lo + 1));
export const list = (rng: () => number, n: number, lo: number, hi: number) => Array.from({ length: n }, () => pick(rng, lo, hi));
export const sortedOnly = (label: string, a: number[]) => {
  for (let i = 1; i < a.length; i++) if (a[i] < a[i - 1]) return `${label} must be sorted from small to large: ${a[i]} comes after ${a[i - 1]}.`;
  return null;
};
