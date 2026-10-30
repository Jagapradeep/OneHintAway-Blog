import Link from "next/link";
import type { PostMeta } from "@/lib/posts";

const pad = (n: number) => String(n).padStart(2, "0");

// A list of post cards: number, title, pattern and the one-line summary.
export function PostList({ posts, showPattern = true }: { posts: PostMeta[]; showPattern?: boolean }) {
  return (
    <ul className="post-list">
      {posts.map((p) => (
        <li key={p.slug}>
          <Link href={`/posts/${p.slug}/`} className="post-card">
            <span className="post-card-num">{pad(p.number)}</span>
            <span className="post-card-text">
              <span className="post-card-title">{p.title}</span>
              {showPattern && p.pattern !== "Roadmap" && <span className="post-card-pattern">{p.pattern}</span>}
              <span className="post-card-summary">{p.summary}</span>
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
