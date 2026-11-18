// Word search: mark a tile while the path stands on it, explore its neighbours,
// unmark it on the way back (post 39). Marked tiles show "#", as in the code; the
// path the search stands on is lit. Neighbours are tried down, up, right, left.
import type { Answer, ArrayView, Cell, GridView, Input, Pattern, Step } from "../schema.ts";
import { arr, pick, sayOk, step, tiles } from "./_lib.ts";

const pseudocode = [
  "function walk(grid, word, row, col, i):",
  "    if grid[row][col] != word[i]:",
  "        return false",
  "    if i == length(word) - 1:",
  "        return true   // last letter matched",
  "    grid[row][col] = \"#\"   // in use",
  "    for each [r, c] next to [row, col]:",
  "        if walk(grid, word, r, c, i + 1):",
  "            return true",
  "    grid[row][col] = word[i]   // undo",
  "    return false",
  "",
  "function exist(grid, word):",
  "    for each cell [row, col] in grid:",
  "        if walk(grid, word, row, col, 0):",
  "            return true",
  "    return false",
];

const MOVES = [[1, 0], [-1, 0], [0, 1], [0, -1]]; // down, up, right, left

function* run(input: Input): Generator<Step, Answer, void> {
  const letters = (input.letters as string).toUpperCase();
  const word = (input.word as string).toUpperCase();
  const cols = input.cols as number;
  const rows = letters.length / cols;
  const grid = [...letters];
  const wt = tiles([...word]);
  let focus = -1, wi = -1;
  const snap = (line: number, say: string) => {
    const g: Cell[][] = [];
    for (let r = 0; r < rows; r++) g.push(Array.from({ length: cols }, (_, c) => {
      const k = r * cols + c;
      return { id: `c${k}`, v: grid[k], state: k === focus ? "gold" : grid[k] === "#" ? "steel" : "plain" };
    }));
    return step(line, say, [
      { kind: "grid", id: "grid", label: "Grid: # = on the path", rows: g },
      arr("word", wt, (i) => (i === wi ? "gold" : i < wi ? "steel" : "plain"), wi >= 0 ? [{ id: "i", label: "i", at: wi }] : [], { label: "word" }),
    ]);
  };

  function* walk(r: number, c: number, i: number): Generator<Step, boolean, void> {
    const k = r * cols + c;
    focus = k;
    wi = i;
    const where = `Row ${r}, column ${c}`;
    if (grid[k] !== word[i]) {
      yield snap(2, grid[k] === "#" ? `${where} is already on the path (#): return false.` : `${where} holds ${grid[k]}, not ${word[i]}: return false.`);
      return false;
    }
    if (i === word.length - 1) {
      yield snap(4, `${where} holds ${word[i]}, the last letter: return true.`);
      return true;
    }
    grid[k] = "#";
    yield snap(5, `${where} holds ${word[i]}, letter ${i} of the word: mark it # while the path uses it.`);
    for (const [dr, dc] of MOVES) {
      const nr = r + dr, nc = c + dc;
      if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
      if (yield* walk(nr, nc, i + 1)) return true;
    }
    grid[k] = word[i];
    focus = k;
    wi = i;
    yield snap(9, `No neighbour goes on from ${word[i]}: unmark row ${r}, column ${c} and step back.`);
    return false;
  }

  yield snap(13, `Try every tile as the first letter, ${word[0]}, row by row.`);
  for (let k = 0; k < letters.length; k++) {
    if (yield* walk(Math.floor(k / cols), k % cols, 0)) {
      wi = -1;
      yield snap(15, `The path spells ${word}: return true.`);
      return true;
    }
  }
  focus = -1;
  wi = -1;
  yield snap(16, `No tile starts a path that spells ${word}: return false.`);
  return false;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const letters = (input.letters as string).toUpperCase();
  const word = (input.word as string).toUpperCase();
  const cols = input.cols as number;
  const g = s.views[0] as GridView, w = s.views[1] as ArrayView;
  if (s.views.length !== 2 || g.kind !== "grid" || w?.id !== "word") return "needs the grid and the word";
  const flat = g.rows.flat();
  if (flat.length !== letters.length || flat.some((c, k) => c.v !== letters[k] && c.v !== "#")) return "a tile holds its letter or #";
  // The marked tiles are the start of the word, each next to the one before: find such an order.
  const marked = flat.flatMap((c, k) => (c.v === "#" ? [k] : []));
  const near = (a: number, b: number) => Math.abs(Math.floor(a / cols) - Math.floor(b / cols)) + Math.abs((a % cols) - (b % cols)) === 1;
  const chain = (have: number[]): boolean =>
    have.length === marked.length || marked.some((k) => !have.includes(k) && letters[k] === word[have.length] && (have.length === 0 || near(have[have.length - 1], k)) && chain([...have, k]));
  if (marked.length >= word.length || !chain([])) return "the # tiles must spell the start of the word along a path";
  if (flat.some((c) => (c.state === "steel") !== (c.v === "#" && c.state !== "gold"))) return "the lit tiles are the # tiles";
  const gold = flat.flatMap((c, k) => (c.state === "gold" ? [k] : []));
  const i = w.pointers[0]?.at;
  if (s.line === 2 || s.line === 4 || s.line === 5 || s.line === 9) {
    if (gold.length !== 1 || i === undefined) return "a walk step lights its tile and the letter it needs";
    const k = gold[0];
    if (s.line === 2 && flat[k].v === word[i]) return "'return false' on a tile that matches";
    if (s.line === 4 && (letters[k] !== word[i] || i !== word.length - 1)) return "'return true' only on the last letter";
    if (s.line === 5 && (flat[k].v !== "#" || letters[k] !== word[i] || marked.length !== i + 1)) return "a matching tile is marked # and ends the path";
    if (s.line === 9 && (flat[k].v === "#" || marked.length !== i)) return "an unmarked tile gets its letter back";
    if (marked.length > 0 && s.line !== 5 && i > 0 && !marked.some((m) => near(m, k))) return "the walk only steps to a neighbour of the path";
  }
  if (isLast !== (s.line === 15 || s.line === 16)) return "the trace must end on a return line";
  return sayOk(input, s, prev);
}

export const wordSearch: Pattern = {
  id: "word-search",
  title: "Word search",
  blurb: "Mark the tile, explore its neighbours, unmark it: backtracking on a grid.",
  problem: "Can a path of touching tiles, each used once, spell the word?",
  section: "Backtracking",
  tier: "paid",
  pseudocode,
  fields: [
    { name: "letters", label: "Letters, row after row", kind: "text", min: 0, max: 0, minLen: 1, maxLen: 6 },
    { name: "cols", label: "Per row", kind: "int", min: 1, max: 3 },
    { name: "word", label: "Word", kind: "text", min: 0, max: 0, minLen: 1, maxLen: 4 },
  ],
  example: { letters: "CATART", cols: 3, word: "CAT" },
  validate(input) {
    const n = (input.letters as string).length;
    const cols = input.cols as number;
    if (n % cols !== 0) return `${n} letters can't fill rows of ${cols}.`;
    return n / cols > 3 ? "At most 3 rows: use fewer letters or a longer row." : null;
  },
  random(rng) {
    const grids = [["CATART", 3], ["SEEDAR", 3], ["TOPSPO", 3], ["DOGOGD", 2], ["MAPAMP", 3], ["ABCESF", 3]] as const;
    const words = ["CAT", "TRAC", "SEE", "SEED", "TOP", "POTS", "DOG", "GOD", "MAP", "PAM", "ABC", "FEB"];
    const [letters, cols] = grids[pick(rng, 0, grids.length - 1)];
    return { letters, cols, word: words[pick(rng, 0, words.length - 1)] };
  },
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => (a ? "The word is in the grid: true" : "Not in the grid: false"),
};
