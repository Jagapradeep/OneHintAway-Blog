// Course helper (chapter 3): run one visualizer pattern in Node and print its steps.
// From site/:
//   node --experimental-strip-types ../docs/learn/try/steps.mjs two-pointers
//   node --experimental-strip-types ../docs/learn/try/steps.mjs two-pointers '{"numbers":[2,7,11,15],"target":9}'
// With no input it uses the pattern's own example. Nothing here is part of the site.
const { patternById, patterns } = await import("../../../site/visualizer/registry.ts");

const [id, json] = process.argv.slice(2);
const pattern = id && patternById(id);
if (!pattern) {
  console.log("Pattern ids:", patterns.map((p) => p.id).join(", "));
  process.exit(id ? 1 : 0);
}

const input = json ? JSON.parse(json) : pattern.example;
const problem = pattern.validate(input);
if (problem) {
  console.log("validate() refused this input:", problem);
  process.exit(1);
}

// run() is a generator: each yield is one step, the return value is the answer.
const gen = pattern.run(input);
const steps = [];
let r = gen.next();
while (!r.done) {
  steps.push(r.value);
  r = gen.next();
}

steps.forEach((step, i) => {
  // check() is the pattern's own rule book, written separately from run().
  const issue = pattern.check(input, step, steps[i - 1] ?? null, i === steps.length - 1);
  const no = String(i + 1).padStart(3);
  console.log(`${no}  line ${String(step.line).padStart(2)}  ${step.say}${issue ? `   ✗ check(): ${issue}` : ""}`);
});
console.log(`\nanswer: ${pattern.answerText(r.value)}   (${steps.length} steps)`);
