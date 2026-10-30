import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";

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
};

const POSTS_DIR = path.join(process.cwd(), "content", "posts");

// Reads every post's frontmatter at build time, sorted by post number.
export function getAllPosts(): PostMeta[] {
  return fs
    .readdirSync(POSTS_DIR)
    .filter((f) => f.endsWith(".mdx"))
    .map((f) => {
      const { data } = matter(fs.readFileSync(path.join(POSTS_DIR, f), "utf8"));
      const published =
        data.published instanceof Date ? data.published.toISOString().slice(0, 10) : String(data.published);
      return { ...data, published, file: f.replace(/\.mdx$/, "") } as PostMeta;
    })
    .sort((a, b) => a.number - b.number);
}

export function getPost(slug: string): PostMeta | undefined {
  return getAllPosts().find((p) => p.slug === slug);
}

// Previous and next post in roadmap (number) order.
export function getNeighbours(slug: string): { prev?: PostMeta; next?: PostMeta } {
  const posts = getAllPosts();
  const i = posts.findIndex((p) => p.slug === slug);
  return { prev: posts[i - 1], next: posts[i + 1] };
}
