// Adds one finished post from the dsa-post skill to the blog (blog content contract v1).
//
//   npm run add-post -- <NN-slug.mdx> <NN-topic-slides.zip | folder of slides>
//
// Copies the MDX to content/posts/, puts slide-NN.png / slide-NN.mp4 in public/posts/NN/
// (a zip may hold them in a subfolder), then checks the post against the contract.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import matter from "gray-matter";

const ROOT = path.join(import.meta.dirname, "..");
const [mdxPath, slidesPath] = process.argv.slice(2);
if (!mdxPath || !slidesPath) {
  console.error("Usage: npm run add-post -- <NN-slug.mdx> <NN-topic-slides.zip | slides folder>");
  process.exit(1);
}
const pad = (n) => String(n).padStart(2, "0");

const raw = fs.readFileSync(mdxPath, "utf8");
const { data: fm } = matter(raw);
if (!Number.isInteger(fm.number) || typeof fm.slug !== "string") {
  console.error(`${mdxPath}: frontmatter needs "number" and "slug" (see the blog content contract).`);
  process.exit(1);
}
const name = `${pad(fm.number)}-${fm.slug}.mdx`;

// 1. Slides: unzip to a temp folder if needed, then collect slide-NN.png / .mp4 from anywhere inside.
let source = slidesPath;
let temp = null;
if (fs.statSync(slidesPath).isFile()) {
  temp = fs.mkdtempSync(path.join(os.tmpdir(), "ohw-slides-"));
  if (process.platform === "win32") {
    // PowerShell's Expand-Archive: always there on Windows (Git Bash's tar misreads "C:" paths).
    const q = (p) => `'${path.resolve(p).replace(/'/g, "''")}'`;
    execFileSync("powershell.exe", ["-NoProfile", "-Command", `Expand-Archive -LiteralPath ${q(slidesPath)} -DestinationPath ${q(temp)} -Force`]);
  } else {
    execFileSync("unzip", ["-o", "-q", slidesPath, "-d", temp]); // macOS and Linux
  }
  source = temp;
}
const found = [];
(function walk(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, e.name);
    if (e.isDirectory() && e.name !== "__MACOSX") walk(full);
    else if (/^slide-\d{2}\.(png|mp4)$/.test(e.name)) found.push(full);
  }
})(source);
if (!found.length) {
  console.error(`No slide-NN.png / slide-NN.mp4 files found in ${slidesPath}.`);
  process.exit(1);
}
const dest = path.join(ROOT, "public", "posts", pad(fm.number));
if (fs.existsSync(dest)) {
  // Replace the old slides completely, so a slide removed from the post doesn't linger.
  for (const f of fs.readdirSync(dest)) if (/^slide-/.test(f)) fs.rmSync(path.join(dest, f));
}
fs.mkdirSync(dest, { recursive: true });
for (const f of found) fs.copyFileSync(f, path.join(dest, path.basename(f)));
if (temp) fs.rmSync(temp, { recursive: true, force: true });

// 2. The post itself. An older file for the same number under another slug is removed.
const postsDir = path.join(ROOT, "content", "posts");
for (const f of fs.readdirSync(postsDir)) {
  if (f.startsWith(pad(fm.number) + "-") && f !== name) {
    console.warn(`Replacing ${f} with ${name}. Its old URL /posts/${f.slice(3, -4)}/ will stop working.`);
    fs.rmSync(path.join(postsDir, f));
  }
}
fs.writeFileSync(path.join(postsDir, name), raw.replace(/\r\n/g, "\n"));
console.log(`Added content/posts/${name} and ${found.length} slide file(s) in public/posts/${pad(fm.number)}/.`);

// 3. Check it.
execFileSync(process.execPath, ["--disable-warning=MODULE_TYPELESS_PACKAGE_JSON", path.join(ROOT, "scripts", "check-posts.mjs"), String(fm.number)], {
  stdio: "inherit",
});
