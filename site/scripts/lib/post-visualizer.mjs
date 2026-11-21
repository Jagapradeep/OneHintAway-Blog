// Which pattern's player belongs on a post, worked out without trusting the post's MDX.
//
// The MDX a post arrives with may lack its `visualizer:` line (the dsa-post skill writes it
// only when the post's kit folder asks for it). So the blog knows it from two other places:
//   1. a pattern file whose `post:` is the post's slug (site/visualizer/patterns/<id>.ts);
//   2. the post's kit folder, post-kit/posts/NN-*/post.json, field blog.visualizer.
// add-post uses this to write the line in; check-visualizer uses it to stop a build where
// a post lost its player. Plain Node (no TypeScript): pattern files are read as text.
import fs from "node:fs";
import path from "node:path";

const SITE = path.join(import.meta.dirname, "..", "..");
const KIT_POSTS = path.join(SITE, "..", "post-kit", "posts");
const pad = (n) => String(n).padStart(2, "0");

let byPost = null; // slug -> [pattern ids whose file says post: <slug>]
function patternsNaming(slug) {
  if (!byPost) {
    byPost = new Map();
    const dir = path.join(SITE, "visualizer", "patterns");
    for (const f of fs.readdirSync(dir).filter((f) => f.endsWith(".ts") && !f.startsWith("_"))) {
      const text = fs.readFileSync(path.join(dir, f), "utf8");
      const id = text.match(/^ {2}id: "([a-z0-9-]+)"/m)?.[1];
      const post = text.match(/^ {2}post: "([a-z0-9-]+)"/m)?.[1];
      if (id && post) byPost.set(post, [...(byPost.get(post) ?? []), id]);
    }
  }
  return byPost.get(slug) ?? [];
}

function kitVisualizer(number) {
  if (!fs.existsSync(KIT_POSTS)) return null; // a checkout without the kit
  const folder = fs.readdirSync(KIT_POSTS).find((f) => f.startsWith(pad(number) + "-"));
  const file = folder && path.join(KIT_POSTS, folder, "post.json");
  if (!file || !fs.existsSync(file)) return null;
  try {
    const id = JSON.parse(fs.readFileSync(file, "utf8"))?.blog?.visualizer;
    return typeof id === "string" && id ? id : null;
  } catch {
    return null;
  }
}

// { id, from } for the player this post should show, { conflict } when the two sources
// disagree, or null when it has none.
export function expectedVisualizer(number, slug) {
  const named = patternsNaming(slug);
  const kit = kitVisualizer(number);
  const ids = [...new Set([...named, ...(kit ? [kit] : [])])];
  if (ids.length > 1) return { conflict: ids };
  if (!ids.length) return null;
  return { id: ids[0], from: named.length ? `visualizer/patterns (post: "${slug}")` : `post-kit/posts/${pad(number)}-*/post.json` };
}

// The MDX with `visualizer: <id>` in its frontmatter, placed before `tags:` as in the contract.
export function withVisualizer(raw, id) {
  const fm = raw.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!fm) return raw;
  const body = fm[1];
  const line = `visualizer: ${id}`;
  const next = /^visualizer:.*$/m.test(body)
    ? body.replace(/^visualizer:.*$/m, line)
    : /^tags:/m.test(body)
      ? body.replace(/^tags:/m, `${line}\ntags:`)
      : `${body}\n${line}`;
  return raw.replace(body, next);
}
