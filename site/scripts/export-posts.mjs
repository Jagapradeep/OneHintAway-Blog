// Writes the list of posts the API searches, and optionally sends it to the API.
//
//   npm run export-posts     write posts-index.json (git-ignored) and stop
//   npm run sync-posts       write it, then PUT it to the API's posts table
//
// The MDX files stay the source of truth. The API's posts table is a copy, replaced as a
// whole on every sync: posts in the list are saved, posts missing from it are deleted.
//
// sync-posts reads API_URL (default http://localhost:8080) and ADMIN_TOKEN from the
// environment; locally the npm script loads them from ../api/.env. The token is never
// passed on the command line, so it can't end up in shell history or a process list.
import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";

const POSTS_DIR = path.join(process.cwd(), "content", "posts");
const OUT = path.join(process.cwd(), "posts-index.json");

// The page's words without its code: search is for ideas, and four language versions of
// the same solution would drown them. Markdown marks go too, so "**trap**" matches "trap".
function plainText(mdx) {
  return mdx
    .replace(/^(`{3,}|~{3,})[\s\S]*?^\1[^\n]*$/gm, " ") // fenced code blocks
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, "$1") // links and images: keep the label
    .replace(/<[^>]+>/g, " ") // tags
    .replace(/^\s*\|?[\s:|-]+\|[\s:|-]*$/gm, " ") // table rule lines
    .replace(/\\([{}<>])/g, "$1") // MDX escapes
    .replace(/[`*_#>|]/g, " ")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&")
    .replace(/\s+/g, " ")
    .trim();
}

const posts = fs
  .readdirSync(POSTS_DIR)
  .filter((f) => f.endsWith(".mdx"))
  .map((f) => {
    const { data, content } = matter(fs.readFileSync(path.join(POSTS_DIR, f), "utf8"));
    return {
      slug: data.slug,
      number: data.number,
      title: data.title,
      pattern: data.pattern,
      section: data.section,
      tags: data.tags ?? [],
      bodyText: `${data.summary ?? ""} ${plainText(content)}`.trim(),
    };
  })
  .sort((a, b) => a.number - b.number);

if (posts.length === 0) {
  console.error("export-posts: no posts found in content/posts");
  process.exit(1);
}
fs.writeFileSync(OUT, JSON.stringify(posts, null, 1));
console.log(`export-posts: ${posts.length} posts written to posts-index.json`);

if (process.argv.includes("--push")) {
  const api = (process.env.API_URL || "http://localhost:8080").replace(/\/+$/, "");
  const token = process.env.ADMIN_TOKEN;
  if (!token) {
    console.error("sync-posts: ADMIN_TOKEN is not set (locally it comes from api/.env)");
    process.exit(1);
  }
  try {
    const res = await fetch(`${api}/api/v1/admin/posts`, {
      method: "PUT",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(posts),
    });
    const text = await res.text();
    if (!res.ok) {
      console.error(`sync-posts: ${api} answered ${res.status}: ${text.slice(0, 300)}`);
      process.exit(1);
    }
    console.log(`sync-posts: ${api} now has these posts: ${text}`);
  } catch (err) {
    console.error(`sync-posts: could not reach ${api} (${err.cause?.code ?? err.message})`);
    process.exit(1);
  }
}
