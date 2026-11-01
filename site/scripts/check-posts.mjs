// Checks every post against the blog content contract shared by the dsa-post and
// onehintaway-blog skills (contract v1.1). Runs before every build (npm "prebuild"),
// so a post that drifts from the contract fails loudly instead of rendering wrong.
//
//   node scripts/check-posts.mjs            check all posts
//   node scripts/check-posts.mjs 21         check one post by number
//
// If the contract changes, change this file, both skills and lib/sections.ts together.
import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import { SECTIONS } from "../lib/sections.ts";

const ROOT = path.join(import.meta.dirname, "..");
const POSTS = path.join(ROOT, "content", "posts");
const MEDIA = path.join(ROOT, "public", "posts");
const LANGS = [
  ["Java", "java"],
  ["Python", "python"],
  ["C++", "cpp"],
  ["JavaScript", "javascript"],
];
const LEVELS = ["easy", "medium", "hard"];
const MAX_FILE = 25 * 1024 * 1024; // Cloudflare Pages per-file limit
const MAX_VIDEO = 5 * 1000 * 1000; // readers are mostly on phones; add-post compresses well under this
const pad = (n) => String(n).padStart(2, "0");

const only = process.argv[2] ? Number(process.argv[2]) : null;
const files = fs.readdirSync(POSTS).filter((f) => f.endsWith(".mdx")).sort();
let errors = 0;
let warnings = 0;
const seenSlugs = new Map();
const seenNumbers = new Map();

for (const file of files) {
  const problems = [];
  const warn = [];
  const err = (m) => problems.push(m);
  const raw = fs.readFileSync(path.join(POSTS, file), "utf8").replace(/\r\n/g, "\n");
  let fm, body;
  try {
    ({ data: fm, content: body } = matter(raw));
  } catch (e) {
    report(file, [`frontmatter is not valid YAML: ${e.message}`], []);
    continue;
  }
  if (only !== null && fm.number !== only) continue;

  // ---- file name and identity
  const m = file.match(/^(\d{2})-([a-z0-9]+(?:-[a-z0-9]+)*)\.mdx$/);
  if (!m) err(`file name must be NN-slug.mdx (two-digit number, lowercase-hyphen slug)`);
  if (!Number.isInteger(fm.number) || fm.number < 0) err(`number must be a whole number, got ${JSON.stringify(fm.number)}`);
  else if (m && Number(m[1]) !== fm.number) err(`number ${fm.number} does not match the file name prefix ${m[1]}`);
  if (typeof fm.slug !== "string" || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(fm.slug)) err(`slug must be lowercase words joined by hyphens`);
  else if (m && m[2] !== fm.slug) err(`slug "${fm.slug}" does not match the file name "${m[2]}"`);
  if (seenSlugs.has(fm.slug)) err(`slug "${fm.slug}" is also used by ${seenSlugs.get(fm.slug)}`);
  if (seenNumbers.has(fm.number)) err(`number ${fm.number} is also used by ${seenNumbers.get(fm.number)}`);
  seenSlugs.set(fm.slug, file);
  seenNumbers.set(fm.number, file);

  // ---- required text fields
  for (const key of ["title", "pattern", "section", "summary"]) {
    if (typeof fm[key] !== "string" || !fm[key].trim()) err(`${key} is missing or empty`);
  }
  if (typeof fm.summary === "string" && fm.summary.length > 160) warn.push(`summary is ${fm.summary.length} characters; keep it to one sentence (160 max)`);
  if (typeof fm.section === "string" && !SECTIONS.some((s) => s.toLowerCase() === fm.section.toLowerCase())) {
    err(`section "${fm.section}" is not one of: ${SECTIONS.join(", ")}`);
  }

  // ---- links
  const checkLink = (l, where) => {
    if (!l || typeof l !== "object") return err(`${where} must be { name, url, ... }`);
    if (typeof l.name !== "string" || !l.name.trim()) err(`${where} has no name`);
    if (typeof l.url !== "string" || !/^https:\/\/\S+$/.test(l.url)) err(`${where} url must start with https://`);
  };
  if (fm.worked !== undefined) checkLink(fm.worked, "worked");
  if (!Array.isArray(fm.practice)) err(`practice must be a list (use practice: [] when there is none)`);
  else
    fm.practice.forEach((p, i) => {
      checkLink(p, `practice[${i}]`);
      if (p && p.level !== undefined && !LEVELS.includes(p.level)) err(`practice[${i}] level must be easy, medium or hard`);
      if (p && fm.worked && p.url === fm.worked.url) err(`practice[${i}] is the worked example; leave it out of practice (the page shows it first)`);
    });

  // ---- tags and date
  if (!Array.isArray(fm.tags) || fm.tags.some((t) => typeof t !== "string" || !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(t))) {
    err(`tags must be a list of lowercase-hyphen words`);
  }
  // Check the date as written: the YAML reader silently rolls 2026-13-45 over into a real date.
  const published = (raw.match(/^published:\s*["']?([^"'\s]+)/m) ?? [])[1] ?? "";
  const asDate = new Date(published + "T00:00:00Z");
  if (!/^\d{4}-\d{2}-\d{2}$/.test(published) || Number.isNaN(asDate.getTime()) || asDate.toISOString().slice(0, 10) !== published) {
    err(`published must be a real date like 2026-10-31 (got "${published}")`);
  }

  // ---- slides and video
  if (!Number.isInteger(fm.slides) || fm.slides < 1 || fm.slides > 20) err(`slides must be a whole number from 1 to 20`);
  if (fm.video !== undefined && (!Number.isInteger(fm.video) || fm.video < 1 || fm.video > fm.slides)) {
    err(`video must be the slide number of the MP4 (1 to ${fm.slides})`);
  }
  if (Number.isInteger(fm.number) && Number.isInteger(fm.slides)) {
    const dir = path.join(MEDIA, pad(fm.number));
    if (!fs.existsSync(dir)) err(`slide folder public/posts/${pad(fm.number)}/ is missing`);
    else {
      const present = new Set(fs.readdirSync(dir));
      for (let n = 1; n <= fm.slides; n++) {
        const want = `slide-${pad(n)}.${n === fm.video ? "mp4" : "png"}`;
        const other = `slide-${pad(n)}.${n === fm.video ? "png" : "mp4"}`;
        if (!present.has(want)) err(present.has(other) ? `slide ${n} is ${other} but frontmatter expects ${want} (check "video")` : `missing public/posts/${pad(fm.number)}/${want}`);
        present.delete(want);
        const full = path.join(dir, want);
        if (fs.existsSync(full) && fs.statSync(full).size > MAX_FILE) err(`${want} is over 25 MB (Cloudflare Pages limit)`);
        else if (want.endsWith(".mp4") && fs.existsSync(full) && fs.statSync(full).size > MAX_VIDEO) {
          warn.push(`${want} is over 5 MB; re-add the post with ffmpeg installed so add-post compresses it`);
        }
      }
      const extra = [...present].filter((f) => /^slide-/.test(f));
      if (extra.length) err(`slide files not counted in "slides": ${extra.join(", ")}`);
    }
  }

  // ---- body
  const lines = body.split("\n");
  const firstText = lines.find((l) => l.trim());
  if (firstText && /^# /.test(firstText)) err(`body starts with a "# title" heading; the page shows the title already, remove it`);

  const headings = [];
  let inFence = false;
  lines.forEach((l, i) => {
    if (/^\s*```/.test(l)) inFence = !inFence;
    else if (!inFence && /^##\s/.test(l)) headings.push({ text: l.replace(/^##\s+/, "").trim(), line: i });
  });
  const langHeads = headings.filter((h) => LANGS.some(([name]) => h.text.startsWith(name)));
  if (fm.pattern !== "Roadmap") {
    const order = langHeads.map((h) => LANGS.find(([name]) => h.text === name || h.text.startsWith(name + " "))?.[0] ?? h.text);
    const expected = LANGS.map(([name]) => name);
    if (order.join(",") !== expected.join(",")) {
      err(`code sections must be "## Java", "## Python", "## C++", "## JavaScript" in that order (found: ${order.join(", ") || "none"})`);
    } else {
      langHeads.forEach((h, k) => {
        const next = langHeads[k + 1]?.line ?? headings.find((x) => x.line > h.line)?.line ?? lines.length;
        const fences = lines.slice(h.line, next).filter((l) => /^\s*```\S/.test(l)).map((l) => l.trim().slice(3));
        if (fences.length !== 1 || fences[0] !== LANGS[k][1]) {
          err(`"## ${h.text}" must hold exactly one \`\`\`${LANGS[k][1]} block (found: ${fences.join(", ") || "none"})`);
        }
      });
    }
    if (!/^```\s*$/m.test(body)) warn.push(`no pseudocode block (an unlabelled \`\`\` fence)`);
  }
  if (headings.some((h) => /^practice\b/i.test(h.text))) {
    warn.push(`"## Practice" section found; practice links belong in frontmatter (the page renders them)`);
  }

  // MDX reads { } as JavaScript and < as a tag: outside code they must be escaped.
  inFence = false;
  lines.forEach((l, i) => {
    if (/^\s*```/.test(l)) return void (inFence = !inFence);
    if (inFence) return;
    const prose = l.split(/(`[^`]*`)/).filter((_, k) => k % 2 === 0).join("");
    const bad = prose.replace(/\\[{}<]/g, "").match(/[{}]|<(?!br\s*\/?>)/);
    if (bad) err(`line ${i + 1}: "${bad[0]}" outside code must be escaped (\\{  \\}  &lt;) or put in backticks: ${l.trim().slice(0, 60)}`);
  });

  report(file, problems, warn);
}

function report(file, problems, warn) {
  errors += problems.length;
  warnings += warn.length;
  for (const p of problems) console.error(`✗ ${file}: ${p}`);
  for (const w of warn) console.warn(`! ${file}: ${w}`);
}

const checked = only === null ? files.length : 1;
if (errors) {
  console.error(`\n${errors} problem(s) in the posts. See the blog content contract in the dsa-post / onehintaway-blog skills.`);
  process.exit(1);
}
console.log(`✓ ${checked} post(s) match the blog content contract${warnings ? ` (${warnings} warning(s))` : ""}.`);
