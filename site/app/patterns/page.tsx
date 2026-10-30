import type { Metadata } from "next";
import { Label, PostList } from "@/components/PostList";
import { getPostsByPattern } from "@/lib/posts";
import { slugify } from "@/lib/sections";

export const metadata: Metadata = {
  title: "Patterns | One Hint Away",
  description: "Every DSA pattern covered so far, A to Z, with the posts that teach it.",
};

// Patterns index: each pattern A to Z with its posts.
export default function PatternsPage() {
  const groups = getPostsByPattern();
  return (
    <>
      <h1 className="chrome">Patterns</h1>
      <p className="lead">Every pattern covered so far, A to Z.</p>

      <nav className="pattern-jump" aria-label="Jump to a pattern">
        {groups.map(({ pattern }) => (
          <a key={pattern} href={`#${slugify(pattern)}`}>
            {pattern}
          </a>
        ))}
      </nav>

      {groups.map(({ pattern, posts }) => (
        <section key={pattern} className="roadmap-section" id={slugify(pattern)}>
          <h2>
            <Label>{pattern}</Label>
          </h2>
          <PostList posts={posts} showPattern={false} />
        </section>
      ))}
    </>
  );
}
