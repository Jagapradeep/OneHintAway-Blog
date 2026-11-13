import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Visualizer } from "@/components/Visualizer";
import { getAllPosts } from "@/lib/posts";
import { patternById, patterns } from "@/visualizer/registry.ts";

type Props = { params: Promise<{ pattern: string }> };

export function generateStaticParams() {
  return patterns.map((p) => ({ pattern: p.id }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const p = patternById((await params).pattern);
  return p ? { title: `${p.title} visualizer | One Hint Away`, description: p.blurb } : {};
}

// One pattern's own page: a short heading, then the player with the screen to itself.
export default async function PatternPage({ params }: Props) {
  const p = patternById((await params).pattern);
  if (!p) notFound();
  // The pattern's post: the one named in the pattern file, or else the post whose
  // frontmatter asks for this player (`visualizer: <id>`), so a newly added post links itself.
  const posts = getAllPosts();
  const post = posts.find((x) => x.slug === p.post) ?? posts.find((x) => x.visualizer === p.id);
  return (
    <article className="prose vz-page vz-one">
      <p className="vz-crumb">
        <Link href="/visualize/">All patterns</Link>
        {post && (
          <>
            {" · "}
            <Link href={`/posts/${post.slug}/`}>Read the post</Link>
          </>
        )}
      </p>
      <h1 className="chrome">{p.title}</h1>
      <Visualizer pattern={p.id} />
    </article>
  );
}
