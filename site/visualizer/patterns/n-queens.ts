// N-queens: one queen per row, a safe test against the rows above, and back up
// when a row has no safe column (post 40). Gold is the square being tried, and the
// queen that attacks it when there is one.
import type { Answer, Cell, GridView, Input, Pattern, Step } from "../schema.ts";
import { varOf } from "../schema.ts";
import { pick, sayOk, step } from "./_lib.ts";

const pseudocode = [
  "function safe(queens, row, col):",
  "    for r from 0 to row - 1:",
  "        c = queens[r]",
  "        gap = row - r",
  "        if col == c:",
  "            return false   // same column",
  "        if col == c + gap or col == c - gap:",
  "            return false   // same diagonal",
  "    return true",
  "function place(queens, row, n, out):",
  "    if row == n:",
  "        add a board of queens to out",
  "        return",
  "    for col from 0 to n - 1:",
  "        if safe(queens, row, col):",
  "            queens[row] = col   // a queen",
  "            place(queens, row + 1, n, out)",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const n = input.n as number;
  const queens: number[] = [];
  const boards: string[] = [];
  let row = 0, col: number | "" = "";
  let tried = -1, hit = -1, put = false, all = false;
  const snap = (line: number, say: string) => {
    const rows: Cell[][] = [];
    for (let r = 0; r < n; r++) rows.push(Array.from({ length: n }, (_, c) => {
      const queen = r < queens.length && queens[r] === c;
      const here = r === row && c === tried;
      const v = queen || (here && put) ? "Q" : "";
      return { id: `q${r}_${c}`, v, state: here || (queen && (r === hit || all)) ? "gold" : queen ? "steel" : "plain" };
    }));
    return step(line, say, [{ kind: "grid", id: "board", label: `Board, ${n} by ${n}`, rows } as GridView], { row, col, boards: boards.length });
  };

  function* place(): Generator<Step, void, void> {
    if (row === n) {
      boards.push(queens.join(" "));
      all = true;
      yield snap(11, `All ${n} rows hold a queen: save the board ${queens.join(" ")}.`);
      all = false;
      return;
    }
    for (let c = 0; c < n; c++) {
      col = c;
      tried = c;
      put = false;
      hit = -1;
      for (let r = 0; r < row; r++) {
        if (queens[r] === c || Math.abs(queens[r] - c) === row - r) {
          hit = r;
          break;
        }
      }
      if (hit >= 0) {
        yield queens[hit] === c
          ? snap(5, `Row ${row}, column ${c}: the queen in row ${hit} has the same column. Not safe.`)
          : snap(7, `Row ${row}, column ${c}: the queen in row ${hit} is on a diagonal. Not safe.`);
        continue;
      }
      put = true;
      yield snap(15, `Row ${row}, column ${c} is safe: put a queen there.`);
      queens.push(c);
      row++;
      tried = -1;
      put = false;
      yield* place();
      row--;
      queens.pop();
    }
    tried = -1;
    hit = -1;
    col = "";
    if (row > 0) yield snap(13, `Row ${row} has no column left to try: back up to row ${row - 1}.`);
  }

  yield snap(9, `Start at row 0 with an empty ${n} by ${n} board.`);
  yield* place();
  yield snap(13, `Every column of row 0 is tried: ${boards.length} board${boards.length === 1 ? "" : "s"} in all.`);
  return boards.length ? boards.join(" | ") : "none";
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const n = input.n as number;
  const g = s.views[0] as GridView;
  if (s.views.length !== 1 || g.kind !== "grid" || g.rows.length !== n || g.rows.some((r) => r.length !== n)) return `needs one ${n} by ${n} board`;
  const row = varOf(s, "row") as number, col = varOf(s, "col");
  // Queens: at most one per row, only in the rows above `row` (plus the one being put down).
  const qs: [number, number][] = [];
  g.rows.forEach((r, y) => r.forEach((c, x) => c.v === "Q" && qs.push([y, x])));
  if (g.rows.some((r) => r.filter((c) => c.v === "Q").length > 1)) return "two queens in one row";
  const attacks = (a: [number, number], b: [number, number]) => a[1] === b[1] || Math.abs(a[1] - b[1]) === Math.abs(a[0] - b[0]);
  for (const a of qs) for (const b of qs) if (a !== b && attacks(a, b)) return `queens at ${a} and ${b} attack each other`;
  const above = qs.filter(([y]) => y < row).length;
  if (above !== Math.min(row, n)) return `rows 0 to ${row - 1} must each hold a queen`;
  const gold = g.rows.flatMap((r, y) => r.flatMap((c, x) => (c.state === "gold" ? [[y, x] as [number, number]] : [])));
  if (s.line === 5 || s.line === 7) {
    const t = gold.find(([y]) => y === row), q = gold.find(([y]) => y < row);
    if (!t || !q || t[1] !== col || g.rows[q[0]][q[1]].v !== "Q") return "a failed test lights the square and the queen that attacks it";
    if (s.line === 5 ? q[1] !== t[1] : q[1] === t[1] || Math.abs(q[1] - t[1]) !== row - q[0]) return "the attack named is not the one shown";
  }
  if (s.line === 15) {
    const t = gold.find(([y]) => y === row);
    if (!t || t[1] !== col || g.rows[row][t[1]].v !== "Q" || qs.some((q) => q[0] < row && attacks(q, t))) return "a queen is put only on a safe square";
  }
  if (s.line === 11 && (row !== n || qs.length !== n)) return "a board is saved with a queen in every row";
  const boards = varOf(s, "boards") as number;
  if (prev && (boards < (varOf(prev, "boards") as number) || boards > (varOf(prev, "boards") as number) + 1)) return "boards are counted one at a time";
  if (isLast !== (s.line === 13 && row === 0)) return "the trace ends once row 0 has tried every column";
  return sayOk(input, s, prev);
}

export const nQueens: Pattern = {
  id: "n-queens",
  title: "N-queens",
  blurb: "One queen per row, test against the rows above, back up when a row runs out.",
  problem: "Place n queens on an n by n board so no two attack each other, and list every way.",
  section: "Backtracking",
  tier: "paid",
  pseudocode,
  fields: [{ name: "n", label: "Board size n", kind: "int", min: 1, max: 4 }],
  example: { n: 4 },
  validate: () => null,
  random: (rng) => ({ n: pick(rng, 3, 4) }),
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => (a === "none" ? "No board works" : `${String(a).split("|").length} boards (queen columns, row by row): ${a}`),
};
