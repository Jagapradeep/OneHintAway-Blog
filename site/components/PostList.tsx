import Link from "next/link";
import type { PostMeta } from "@/lib/posts";
import { pad2 } from "@/lib/sections";

// A list of post cards: number, title, pattern and the one-line summary.
// `grid` lays the cards out in two columns on wide screens.
export function PostList({
  posts,
  showPattern = true,
  grid = false,
}: {
  posts: PostMeta[];
  showPattern?: boolean;
  grid?: boolean;
}) {
  return (
    <ul className={grid ? "post-list post-grid" : "post-list"}>
      {posts.map((p) => (
        <li key={p.slug}>
          <Link href={`/posts/${p.slug}/`} className="post-card">
            <span className="post-card-num">{pad2(p.number)}</span>
            <span className="post-card-text">
              {showPattern && p.pattern !== "Roadmap" && <span className="post-card-pattern">{p.pattern}</span>}
              <span className="post-card-title">{p.title}</span>
              <span className="post-card-summary">{p.summary}</span>
            </span>
            <span className="post-card-arrow" aria-hidden="true">
              →
            </span>
          </Link>
        </li>
      ))}
    </ul>
  );
}

// Small mono caps pill with a glowing dot, like the section labels on the slides.
export function Label({ children, gold = false }: { children: React.ReactNode; gold?: boolean }) {
  return <span className={gold ? "label label-gold" : "label"}>{children}</span>;
}
