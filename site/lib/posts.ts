import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import { sectionIndex } from "./sections";

export type PracticeLink = {
  name: string;
  url: string;
  level?: "easy" | "medium" | "hard";
  note?: string; // one-line hint shown under the link
};

export type PostMeta = {
  number: number;
  title: string;
  slug: string;
  pattern: string;
  section: string;
  summary: string;
  worked?: { name: string; url: string };
  practice: PracticeLink[];
  slides: number;
  video?: number;
  tags: string[];
  published: string;
  file: string; // file name without .mdx, e.g. "00-start-here"
  hasCode: boolean; // the body has the four-language code tabs
};

const POSTS_DIR = path.join(process.cwd(), "content", "posts");

// Reads every post's frontmatter at build time, sorted by post number.
export function getAllPosts(): PostMeta[] {
  return fs
    .readdirSync(POSTS_DIR)
    .filter((f) => f.endsWith(".mdx"))
    .map((f) => {
      const { data, content } = matter(fs.readFileSync(path.join(POSTS_DIR, f), "utf8"));
      const published =
        data.published instanceof Date ? data.published.toISOString().slice(0, 10) : String(data.published);
      return { ...data, published, file: f.replace(/\.mdx$/, ""), hasCode: /^## Java\s*$/m.test(content) } as PostMeta;
    })
    .sort((a, b) => a.number - b.number);
}

export function getPost(slug: string): PostMeta | undefined {
  return getAllPosts().find((p) => p.slug === slug);
}

// Posts grouped by roadmap section, sections in roadmap order, posts by number.
export function getPostsBySection(): { section: string; posts: PostMeta[] }[] {
  const groups = new Map<string, PostMeta[]>();
  for (const p of getAllPosts()) {
    const list = groups.get(p.section) ?? [];
    list.push(p);
    groups.set(p.section, list);
  }
  return [...groups.entries()]
    .sort(([a], [b]) => sectionIndex(a) - sectionIndex(b) || a.localeCompare(b))
    .map(([section, posts]) => ({ section, posts }));
}

// Posts grouped by pattern, patterns A to Z. The "Roadmap" post (00) is left out.
export function getPostsByPattern(): { pattern: string; posts: PostMeta[] }[] {
  const groups = new Map<string, PostMeta[]>();
  for (const p of getAllPosts()) {
    if (p.pattern === "Roadmap") continue;
    const list = groups.get(p.pattern) ?? [];
    list.push(p);
    groups.set(p.pattern, list);
  }
  return [...groups.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([pattern, posts]) => ({ pattern, posts }));
}

// Previous and next post in roadmap (number) order.
export function getNeighbours(slug: string): { prev?: PostMeta; next?: PostMeta } {
  const posts = getAllPosts();
  const i = posts.findIndex((p) => p.slug === slug);
  return { prev: posts[i - 1], next: posts[i + 1] };
}

// Numbers for the home page: lessons, patterns, practice problems.
export function getSiteStats(): { posts: number; patterns: number; problems: number } {
  const posts = getAllPosts();
  const patterns = new Set(posts.map((p) => p.pattern).filter((p) => p !== "Roadmap" && p !== "Foundations"));
  const problems = posts.reduce((n, p) => n + p.practice.length + (p.worked ? 1 : 0), 0);
  return { posts: posts.length, patterns: patterns.size, problems };
}
