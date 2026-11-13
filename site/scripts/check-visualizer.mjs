// Checks the visualizer engine before every build. For each pattern:
//   1. differential: the TypeScript answer agrees with ref.py's brute force
//      on every test input in the fixture;
//   2. invariants: every step of every input obeys the schema rules and the
//      pattern's own rules (pointers in bounds, narration matches state, …);
//   3. snapshot: the example's step trace equals ref.py's viz_steps() exactly;
//   4. the pseudocode equals the pseudocode in the pattern's post;
//   5. the "random example" generator only produces valid inputs.
// Fixtures come from `npm run viz-fixtures` (Python). Options: --sample N
// checks N cases per pattern (for quick runs while developing).
import { existsSync, readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { loaders } from "../visualizer/loaders.ts";
import { patterns } from "../visualizer/registry.ts";
import { SCHEMA_VERSION, checkLimits, checkStep, traceOf } from "../visualizer/schema.ts";

const site = join(dirname(fileURLToPath(import.meta.url)), "..");
const sampleAt = process.argv.indexOf("--sample");
const sample = sampleAt > 0 ? Number(process.argv[sampleAt + 1]) : 0;
const errors = [];
const MAX_ERRORS_PER_PATTERN = 5;

const canon = (v) =>
  JSON.stringify(v, (_k, x) => (x && typeof x === "object" && !Array.isArray(x) ? Object.fromEntries(Object.keys(x).sort().map((k) => [k, x[k]])) : x));
const short = (v) => {
  const s = JSON.stringify(v);
  return s.length > 160 ? s.slice(0, 160) + "…" : s;
};

function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Runs one input through the engine and every invariant. Returns the trace. */
function checked(p, input, fail) {
  const bad = p.validate(input);
  if (bad) return fail(`input breaks the pattern's own rule: ${bad}`);
  let trace;
  try {
    trace = traceOf(p, input);
  } catch (e) {
    return fail(`run() threw: ${e.message}`);
  }
  if (trace.steps.length === 0) return fail("no steps");
  for (let i = 0; i < trace.steps.length; i++) {
    const why = checkStep(trace, i) ?? p.check(input, trace.steps[i], i ? trace.steps[i - 1] : null, i === trace.steps.length - 1);
    if (why) return fail(`step ${i + 1} of ${trace.steps.length}: ${why}\n      narration: "${trace.steps[i].say}"`);
  }
  return trace;
}

function postPseudocode(slug) {
  const dir = join(site, "content", "posts");
  const file = readdirSync(dir).find((f) => f.replace(/^\d+-/, "") === `${slug}.mdx`);
  if (!file) return null;
  const m = readFileSync(join(dir, file), "utf8").match(/^## Pseudocode\r?\n[\s\S]*?\n```\r?\n([\s\S]*?)\r?\n```/m);
  return m ? m[1].split(/\r?\n/) : null;
}

// A post asks for a player with the frontmatter line `visualizer: <pattern id>`.
const postsDir = join(site, "content", "posts");
let embeds = 0;
const embedOf = {}; // pattern id -> slug of the first post that shows its player
for (const file of readdirSync(postsDir).filter((f) => f.endsWith(".mdx")).sort()) {
  const fm = readFileSync(join(postsDir, file), "utf8").match(/^---\r?\n([\s\S]*?)\r?\n---/);
  const m = fm?.[1].match(/^visualizer:[ \t]*(.*)$/m);
  if (!m) continue;
  embeds++;
  const id = m[1].trim().replace(/^["']|["']$/g, "");
  embedOf[id] ??= file.replace(/^\d+-/, "").replace(/\.mdx$/, "");
  if (!patterns.some((p) => p.id === id)) errors.push(`${file}: visualizer "${id}" is not a pattern. Known: ${patterns.map((p) => p.id).join(", ")}`);
}

// The browser's loaders must cover exactly the patterns in the registry.
for (const id of new Set([...Object.keys(loaders), ...patterns.map((p) => p.id)])) {
  if (!loaders[id]) errors.push(`${id}: missing from visualizer/loaders.ts`);
  else if (!patterns.some((p) => p.id === id)) errors.push(`${id}: in loaders.ts but not in registry.ts`);
  else if ((await loaders[id]()) !== patterns.find((p) => p.id === id)) errors.push(`${id}: loaders.ts loads a different pattern`);
}
for (const p of patterns) if (p.tier !== "free" && p.tier !== "paid") errors.push(`${p.id}: tier must be "free" or "paid"`);

let total = 0;
const ids = new Set();
for (const p of patterns) {
  const at = errors.length;
  const fail = (where) => (msg) => {
    if (errors.length - at < MAX_ERRORS_PER_PATTERN) errors.push(`${p.id}: ${where}: ${msg}`);
    return null;
  };
  if (ids.has(p.id)) errors.push(`${p.id}: listed twice in registry.ts`);
  ids.add(p.id);

  const limits = checkLimits(p.fields, p.example);
  if (limits) fail("example")(limits);

  // The pattern's post: named in the pattern file, or else the post that embeds this player.
  const slug = p.post ?? embedOf[p.id];
  if (slug) {
    const want = postPseudocode(slug);
    if (!want) fail("pseudocode")(`post "${slug}" or its ## Pseudocode block was not found`);
    else if (want.join("\n") !== p.pseudocode.join("\n")) fail("pseudocode")(`differs from the pseudocode in the "${slug}" post`);
  }

  const file = join(site, "visualizer", "fixtures", `${p.id}.json`);
  if (!existsSync(file)) {
    errors.push(`${p.id}: no fixture. Run: npm run viz-fixtures`);
    continue;
  }
  const fx = JSON.parse(readFileSync(file, "utf8"));
  if (fx.schema !== SCHEMA_VERSION) fail("fixture")(`schema ${fx.schema}, the engine is on ${SCHEMA_VERSION}. Run: npm run viz-fixtures`);

  // Snapshot: the example, step by step, against Python's viz_steps().
  if (canon(fx.example.input) !== canon(p.example)) fail("example")(`ref.py's EXAMPLE ${short(fx.example.input)} is not the pattern's example ${short(p.example)}`);
  const ex = checked(p, p.example, fail("example"));
  if (ex && !fx.example.steps) {
    // A ref.py without viz_steps(): only the example's answer is compared.
    if (!p.sameAnswer(p.example, ex.answer, fx.example.answer)) fail("example")(`answer ${short(ex.answer)}, ref.py's brute force says ${short(fx.example.answer)}`);
  } else if (ex) {
    const want = fx.example;
    if (canon(ex.pseudocode) !== canon(want.pseudocode)) fail("snapshot")("pseudocode differs from ref.py's PSEUDOCODE");
    if (ex.steps.length !== want.steps.length) fail("snapshot")(`${ex.steps.length} steps, ref.py has ${want.steps.length}`);
    for (let i = 0; i < Math.min(ex.steps.length, want.steps.length); i++) {
      if (canon(ex.steps[i]) !== canon(want.steps[i])) {
        fail("snapshot")(`step ${i + 1} differs from ref.py\n      ts: ${short(ex.steps[i])}\n      py: ${short(want.steps[i])}`);
        break;
      }
    }
    if (canon(ex.answer) !== canon(want.answer)) fail("snapshot")(`answer ${short(ex.answer)}, ref.py has ${short(want.answer)}`);
  }

  // Differential + invariants on every test input.
  if (fx.cases.length < 1000) fail("fixture")(`only ${fx.cases.length} test inputs (at least 1,000 needed)`);
  const step = sample ? Math.max(1, Math.floor(fx.cases.length / sample)) : 1;
  let ran = 0;
  for (let i = 0; i < fx.cases.length; i += step) {
    const c = fx.cases[i];
    const f = fail(`test input ${i + 1} ${short(c.in)}`);
    const t = checked(p, c.in, f);
    if (t && !p.sameAnswer(c.in, t.answer, c.out)) f(`answer ${short(t.answer)}, brute force says ${short(c.out)}`);
    ran++;
  }

  // The "random example" button: always a valid input that runs clean.
  const rng = mulberry32(20261111);
  for (let i = 0; i < (sample ? 50 : 500); i++) {
    const input = p.random(rng);
    const f = fail(`random input ${short(input)}`);
    const lim = checkLimits(p.fields, input);
    if (lim) f(lim);
    else checked(p, input, f);
  }

  total += ran;
  if (errors.length === at) console.log(`check-visualizer: ${p.id} ok (${ran}${sample ? ` of ${fx.cases.length}` : ""} test inputs, ${ex.steps.length} example steps)`);
}

if (errors.length) {
  console.error(`check-visualizer: ${errors.length} problem(s)\n`);
  for (const e of errors) console.error(`  ${e}`);
  process.exit(1);
}
console.log(`check-visualizer: ${patterns.length} pattern(s), ${total} test inputs, all steps valid, ${embeds} post(s) with a player`);
