// check_mdx.mjs (v2, 1 November 2026): checks one post's NN-slug.mdx against the blog content
// contract (section 10) and the writing rules (section 11) before it goes to Jaga.
//   node check_mdx.mjs NN-slug.mdx --slides <zip|folder> --pseudo pseudo.txt --extract code/
// Exit 0 = no errors (read the warnings). Exit 1 = errors: fix and run again.
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import matter from "gray-matter";
import { compile } from "@mdx-js/mdx";
import remarkGfm from "remark-gfm";
import remarkFrontmatter from "remark-frontmatter";

const SECTIONS = ["Start here", "Foundations", "Arrays and hashing", "Maths", "Recursion and sorting", "Binary search",
  "2D arrays and strings", "Backtracking", "Linked list", "Bit manipulation", "Greedy", "Stack and queue", "Trees",
  "Heaps", "Graphs", "Dynamic programming", "Tries and strings", "Advanced (optional)"];
const PATTERNS = ["Roadmap", "Foundations", "Hashing", "Two pointers", "Sliding window", "Prefix sum", "Kadane's algorithm",
  "Three-way partition", "Moore's voting", "Cyclic sort", "Merge intervals", "Next permutation", "Number theory", "Recursion", "Sorting", "Binary search"];
const FIELDS = ["number", "title", "slug", "pattern", "section", "summary", "worked", "practice", "slides", "video", "visualizer", "tags", "published"];
const LANGS = [["Java", "java"], ["Python", "python"], ["C++", "cpp"], ["JavaScript", "javascript"]];
const HEAD_ORDER = ["The idea", "The walk", "Pseudocode", "Java", "Python", "C++", "JavaScript", "Complexity", "How it was tested"];
const MAX_FILE = 25 * 1024 * 1024;
const NAME_RE = /^(LeetCode \d+ \S.*|GeeksforGeeks \S.*)$/;

const args = process.argv.slice(2);
const file = args.find((a) => a.endsWith(".mdx"));
const opt = (k) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : undefined; };
if (!file) { console.error("usage: node check_mdx.mjs NN-slug.mdx [--slides zip|dir] [--pseudo file] [--extract dir]"); process.exit(2); }

const errors = [], warnings = [];
const err = (m) => errors.push(m), warn = (m) => warnings.push(m);
const raw = fs.readFileSync(file, "utf8");
if (raw.includes("\r")) err("file has Windows line endings (CRLF); write it with \\n only");
const text = raw.replace(/\r\n/g, "\n");
if (!text.startsWith("---\n")) err("file must start with the --- frontmatter line");

// ---------- frontmatter
let fm = {}, body = "";
try { ({ data: fm, content: body } = matter(text)); } catch (e) { err(`frontmatter is not valid YAML: ${e.message}`); }
const base = path.basename(file);
const m = base.match(/^(\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.mdx$/);
if (!m) err(`file name "${base}" must be NN-slug.mdx (two digits, lowercase words joined by hyphens)`);
for (const k of Object.keys(fm)) if (!FIELDS.includes(k)) err(`unknown frontmatter field "${k}" (allowed: ${FIELDS.join(", ")})`);
for (const k of ["number", "title", "slug", "pattern", "section", "summary", "practice", "slides", "tags", "published"]) {
  if (fm[k] === undefined) err(`frontmatter field "${k}" is missing`);
}
if (!Number.isInteger(fm.number)) err(`number must be a whole number`);
else if (m && Number(m[1]) !== fm.number) err(`number ${fm.number} does not match the file name prefix ${m[1]}`);
if (typeof fm.slug !== "string" || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(fm.slug)) err(`slug must be lowercase words joined by hyphens, no number`);
else if (m && m[2] !== fm.slug) err(`slug "${fm.slug}" does not match the file name part "${m[2]}"`);
for (const k of ["title", "pattern", "section", "summary"]) if (typeof fm[k] !== "string" || !fm[k].trim()) err(`${k} must be non-empty text`);
if (typeof fm.section === "string" && !SECTIONS.includes(fm.section)) err(`section "${fm.section}" is not exactly one of: ${SECTIONS.join(", ")}`);
if (typeof fm.pattern === "string" && !PATTERNS.includes(fm.pattern)) {
  warn(`pattern "${fm.pattern}" is new. Fine only if no existing pattern fits; then add it to the contract's pattern list in BOTH skills`);
}
if (typeof fm.summary === "string") {
  if (fm.summary.length > 160) err(`summary is ${fm.summary.length} characters (max 160)`);
  if (/[.!?]\s+[A-Z]/.test(fm.summary)) err(`summary must be one sentence`);
}
if (typeof fm.title === "string" && /^[a-z]/.test(fm.title)) err(`title must start with a capital (sentence case)`);

const checkLink = (l, where, practice) => {
  if (!l || typeof l !== "object") return err(`${where} must be { name, url${practice ? ", level, note" : ""} }`);
  const allowed = practice ? ["name", "url", "level", "note"] : ["name", "url"];
  for (const k of Object.keys(l)) if (!allowed.includes(k)) err(`${where} has unknown key "${k}"`);
  if (typeof l.name !== "string" || !NAME_RE.test(l.name)) err(`${where} name must be "LeetCode N Exact Title" or "GeeksforGeeks Title" (got ${JSON.stringify(l.name)})`);
  if (typeof l.url !== "string" || !/^https:\/\/\S+$/.test(l.url)) err(`${where} url must start with https://`);
  else if (/^LeetCode /.test(l.name ?? "") && !/^https:\/\/leetcode\.com\/problems\/[a-z0-9-]+\/$/.test(l.url)) err(`${where} url must look like https://leetcode.com/problems/<slug>/`);
  else if (/^GeeksforGeeks /.test(l.name ?? "") && !/^https:\/\/www\.geeksforgeeks\.org\//.test(l.url)) err(`${where} url must be on https://www.geeksforgeeks.org/`);
  if (practice) {
    if (!["easy", "medium", "hard"].includes(l.level)) err(`${where} level must be easy, medium or hard`);
    if (typeof l.note !== "string" || !l.note.trim()) err(`${where} note is missing (the slide's one-line hint)`);
  }
};
if (fm.worked !== undefined) checkLink(fm.worked, "worked", false);
if (!Array.isArray(fm.practice)) err(`practice must be a list (practice: [] when there is none)`);
else {
  fm.practice.forEach((p, i) => checkLink(p, `practice[${i}]`, true));
  if (fm.worked && fm.practice.some((p) => p?.url === fm.worked.url)) err(`practice repeats the worked example; leave it out of practice`);
  const urls = fm.practice.map((p) => p?.url); if (new Set(urls).size !== urls.length) err(`practice has the same problem twice`);
}
if (!Array.isArray(fm.tags) || !fm.tags.length || fm.tags.some((t) => typeof t !== "string" || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(t))) err(`tags must be a non-empty list of lowercase-hyphen words`);
const published = (text.match(/^published:\s*["']?([^"'\s]+)/m) ?? [])[1] ?? "";
const d = new Date(published + "T00:00:00Z");
if (!/^\d{4}-\d{2}-\d{2}$/.test(published) || Number.isNaN(d.getTime()) || d.toISOString().slice(0, 10) !== published) err(`published must be a real date YYYY-MM-DD (got "${published}")`);
if (!Number.isInteger(fm.slides) || fm.slides < 1 || fm.slides > 20) err(`slides must be a whole number from 1 to 20`);
if (fm.video !== undefined && (!Number.isInteger(fm.video) || fm.video < 1 || fm.video > fm.slides)) err(`video must be the MP4's slide number (1 to slides)`);
if (fm.visualizer !== undefined && (typeof fm.visualizer !== "string" || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(fm.visualizer))) err(`visualizer must be a pattern id such as two-pointers (the blog build checks it exists)`);

// ---------- slides export
const slidesArg = opt("--slides");
if (slidesArg) {
  let entries = [];
  if (!fs.existsSync(slidesArg)) err(`--slides ${slidesArg} does not exist`);
  else if (fs.statSync(slidesArg).isDirectory()) entries = fs.readdirSync(slidesArg).map((n) => ({ n, size: fs.statSync(path.join(slidesArg, n)).size }));
  else {
    const out = execFileSync("unzip", ["-Zl", slidesArg], { encoding: "utf8" }).split("\n");
    for (const line of out) { const p = line.trim().split(/\s+/); if (p.length >= 10 && /^slide-/.test(p[p.length - 1])) entries.push({ n: p[p.length - 1], size: Number(p[3]) }); }
  }
  entries = entries.filter((e) => /^slide-\d{2}\.(png|mp4)$/.test(e.n));
  const names = new Set(entries.map((e) => e.n));
  for (let i = 1; i <= (fm.slides ?? 0); i++) {
    const want = `slide-${String(i).padStart(2, "0")}.${i === fm.video ? "mp4" : "png"}`;
    if (!names.has(want)) err(`slides export has no ${want} (check "slides" and "video")`);
  }
  if (entries.length !== fm.slides) err(`slides export has ${entries.length} slide files but slides: ${fm.slides}`);
  for (const e of entries) if (e.size > MAX_FILE) err(`${e.n} is over 25 MB (Cloudflare Pages limit)`);
} else warn(`--slides not given: slides, video and file sizes were not checked against the export`);

// ---------- body structure
const lines = body.split("\n");
const heads = []; const fences = []; let open = null;
lines.forEach((l, i) => {
  if (/^\s*```/.test(l)) {
    if (!open) open = { lang: l.trim().slice(3).trim(), start: i, indent: l.match(/^\s*/)[0].length };
    else { fences.push({ ...open, end: i }); open = null; }
  } else if (!open && /^#{1,6}\s/.test(l)) heads.push({ level: l.match(/^#+/)[0].length, text: l.replace(/^#+\s+/, "").trim(), line: i });
});
if (open) err(`a code fence opened on body line ${open.start + 1} is never closed`);
const first = lines.find((l) => l.trim());
if (!first || /^#/.test(first)) err(`body must open with one or two lines (the clue and the worked example), not a heading`);
if (heads.some((h) => h.level === 1)) err(`no "# " heading in the body; the page shows the title`);
const h2 = heads.filter((h) => h.level === 2);
const names2 = h2.map((h) => h.text);
for (const n of names2) if (!HEAD_ORDER.includes(n)) err(`"## ${n}" is not an allowed section (allowed, in order: ${HEAD_ORDER.join(", ")})`);
const idx = names2.map((n) => HEAD_ORDER.indexOf(n)).filter((i) => i >= 0);
if (idx.some((v, i) => i && v <= idx[i - 1])) err(`sections are out of order or repeated (found: ${names2.join(" → ")})`);
for (const n of HEAD_ORDER.slice(2)) if (!names2.includes(n)) err(`"## ${n}" is missing`);
if (!names2.includes("The idea") && !names2.includes("The walk")) err(`add "## The idea" and/or "## The walk"`);
const sectionOf = (name) => {
  const h = h2.find((x) => x.text === name); if (!h) return null;
  const next = h2.find((x) => x.line > h.line); return { from: h.line, to: next ? next.line : lines.length };
};
const inSec = (f, s) => s && f.start > s.from && f.end < s.to;

const unl = fences.filter((f) => f.lang === "");
const ps = sectionOf("Pseudocode");
if (unl.length !== 1) err(`need exactly one unlabelled \`\`\` fence (the pseudocode); found ${unl.length}. Write formulas in backticks instead`);
const pf = unl[0];
if (pf && ps && !inSec(pf, ps)) err(`the pseudocode fence must sit under "## Pseudocode"`);
for (const f of fences) if (f.lang && !LANGS.some(([, id]) => id === f.lang)) err(`fence label "${f.lang}" on body line ${f.start + 1}: use java, python, cpp or javascript only`);
for (const f of fences) if (f.indent) err(`fence on body line ${f.start + 1} is indented; start fences at column 0`);
LANGS.forEach(([name, id], k) => {
  const s = sectionOf(name); if (!s) return;
  const inside = fences.filter((f) => inSec(f, s));
  if (inside.length !== 1 || inside[0].lang !== id) return err(`"## ${name}" must hold exactly one \`\`\`${id} block (found: ${inside.map((f) => f.lang || "unlabelled").join(", ") || "none"})`);
  const f = inside[0];
  const before = lines.slice(s.from + 1, f.start).filter((l) => l.trim());
  if (before.length) err(`"## ${name}": nothing may come between the heading and the code (move notes after the JavaScript block)`);
  const after = lines.slice(f.end + 1, s.to).filter((l) => l.trim());
  if (after.length && name !== "JavaScript") err(`"## ${name}": text after its code block would show inside the ${name} tab; move it after the JavaScript block`);
  if (!lines.slice(f.start + 1, f.end).some((l) => l.trim())) err(`"## ${name}" code block is empty`);
  const HARNESS = {
    java: [/\bstatic\s+void\s+main\s*\(/, /System\.in\b/, /\bBufferedReader\b/, /\bnew\s+Scanner\s*\(/],
    python: [/__name__\s*==/, /\bsys\.stdin\b/, /(^|[^.\w])input\s*\(/],
    cpp: [/\bint\s+main\s*\(/, /\bcin\b/, /\bscanf\s*\(/],
    javascript: [/\bprocess\.stdin\b/, /\breadFileSync\s*\(/, /require\(\s*["']readline["']\s*\)/],
  };
  lines.slice(f.start + 1, f.end).forEach((l, j) => {
    const code = id === "python" ? l.replace(/#.*$/, "") : l.replace(/\/\/.*$/, "");
    if (/(\/\/|#) ---- test harness: not on the blog ----/.test(l)) err(`"## ${name}" body line ${f.start + 2 + j}: the harness line and everything below it stay out of the blog; paste only the part above it`);
    else if ((HARNESS[id] || []).some((r) => r.test(code))) err(`"## ${name}" body line ${f.start + 2 + j}: test harness code ("${l.trim().slice(0, 60)}"); the blog shows the solution only, without main or input reading`);
  });
});
if (ps) {
  const trapLine = lines.findIndex((l, i) => i > (pf?.end ?? ps.from) && i < ps.to && /^\*\*The trap:\*\* \S/.test(l));
  if (trapLine < 0) err(`"**The trap:** …" must follow the pseudocode block, inside "## Pseudocode"`);
}
const tested = sectionOf("How it was tested");
if (tested && !/\d/.test(lines.slice(tested.from + 1, tested.to).join(" "))) err(`"## How it was tested" must say what was run and on how many inputs (no numbers found)`);
const cx = sectionOf("Complexity");
if (cx && !/O\(/.test(lines.slice(cx.from + 1, cx.to).join(" "))) err(`"## Complexity" must state time and space in O(...)`);

// ---------- pseudocode content
if (pf) {
  const pl = lines.slice(pf.start + 1, pf.end);
  pl.forEach((l, i) => {
    if (/\t/.test(l)) err(`pseudocode line ${i + 1} has a tab; use 4 spaces`);
    const code = l.replace(/\/\/.*$/, "");
    if (/\+\+|--(?!\s)|===|!==|;\s*$|\?\s*[^:]+:|\{|\}/.test(code)) err(`pseudocode line ${i + 1} looks language-specific (++, ===, ;, ?:, braces): "${l.trim()}"`);
  });
  const pseudoArg = opt("--pseudo");
  if (pseudoArg) {
    const want = fs.readFileSync(pseudoArg, "utf8").replace(/\r\n/g, "\n").replace(/\n+$/, "").split("\n").map((l) => l.replace(/\s+$/, ""));
    const got = pl.map((l) => l.replace(/\s+$/, ""));
    const n = Math.max(want.length, got.length);
    for (let i = 0; i < n; i++) if (want[i] !== got[i]) { err(`pseudocode differs from the slides at line ${i + 1}: slide "${want[i] ?? "(none)"}", mdx "${got[i] ?? "(none)"}"`); break; }
  } else warn(`--pseudo not given: the pseudocode was not compared with the slides`);
}

// ---------- prose safety
let inF = false;
lines.forEach((l, i) => {
  if (/^\s*```/.test(l)) { inF = !inF; return; }
  if (inF) return;
  const prose = l.split(/(`[^`]*`)/).filter((_, k) => k % 2 === 0).join("");
  const bad = prose.replace(/\\[{}<]/g, "").match(/[{}]|<(?!br\s*\/?>)/);
  if (bad) err(`body line ${i + 1}: "${bad[0]}" outside code must be escaped (\\{  \\}  &lt;) or put in backticks`);
  if (/^#{2,}\s*practice\b/i.test(l)) err(`no "## Practice" section; the page builds it from frontmatter`);
  if (/\]\(\/posts\/[^)]*[^/)]\)/.test(l)) err(`body line ${i + 1}: links to posts must end with "/" (e.g. /posts/two-pointers/)`);
});

// ---------- real MDX compile (what the build does)
try { await compile(text, { remarkPlugins: [remarkFrontmatter, remarkGfm] }); }
catch (e) { err(`MDX does not compile: ${String(e.message || e).split("\n")[0]}${e.line ? ` (file line ${e.line})` : ""}`); }

// ---------- extract code for re-running
const ex = opt("--extract");
if (ex) {
  fs.mkdirSync(ex, { recursive: true });
  const outName = { java: "Main.java", python: "main.py", cpp: "main.cpp", javascript: "main.js" };
  for (const f of fences) if (outName[f.lang]) fs.writeFileSync(path.join(ex, outName[f.lang]), lines.slice(f.start + 1, f.end).join("\n") + "\n");
}

for (const e of errors) console.error(`✗ ${e}`);
for (const w of warnings) console.warn(`! ${w}`);
console.log(errors.length ? `\n${errors.length} error(s) in ${base}. Fix them and run again.` : `✓ ${base} passes (${warnings.length} warning(s))`);
process.exit(errors.length ? 1 : 0);
