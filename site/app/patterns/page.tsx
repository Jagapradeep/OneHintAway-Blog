import type { Metadata } from "next";
import { PatternNav } from "@/components/PatternNav";
import { PostList } from "@/components/PostList";
import { getPostsByPattern } from "@/lib/posts";
import { slugify } from "@/lib/sections";

export const metadata: Metadata = {
  title: "Patterns | One Hint Away",
  description: "Every DSA pattern covered so far, A to Z, with the posts that teach it.",
};

// Patterns index: a sticky list of patterns on the left, each pattern's posts on the right.
export default function PatternsPage() {
  const groups = getPostsByPattern();
  const items = groups.map(({ pattern, posts }) => ({ id: slugify(pattern), name: pattern, count: posts.length }));
  const total = groups.reduce((n, g) => n + g.posts.length, 0);

  return (
    <div className="page-wide">
      <header className="page-head">
        <p className="eyebrow">Patterns A to Z</p>
        <h1 className="chrome">Patterns</h1>
        <p className="lead">
          Know the pattern you need? Pick it from the list. Each one links to the lessons that teach it, with code and
          practice problems.
        </p>
      </header>

      <div className="patterns-layout">
        <PatternNav items={items} total={total} />
        <div className="patterns-content">
          {groups.map(({ pattern, posts }) => (
            <section
              key={pattern}
              className="pattern-section"
              id={slugify(pattern)}
              tabIndex={-1}
              aria-labelledby={`${slugify(pattern)}-title`}
            >
              <div className="section-head">
                <h2 id={`${slugify(pattern)}-title`}>{pattern}</h2>
                <span className="section-count">
                  {posts.length} lesson{posts.length > 1 ? "s" : ""}
                </span>
              </div>
              <PostList posts={posts} showPattern={false} />
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}
