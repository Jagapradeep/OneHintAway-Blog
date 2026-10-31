import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Label } from "@/components/PostList";
import { SlideGallery } from "@/components/SlideGallery";
import { getAllPosts, getNeighbours, getPost } from "@/lib/posts";

type Props = { params: Promise<{ slug: string }> };

const pad = (n: number) => String(n).padStart(2, "0");
const formatDate = (iso: string) =>
  new Date(`${iso}T00:00:00Z`).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });

// One HTML page per post, built ahead of time. Unknown slugs are a 404.
export function generateStaticParams() {
  return getAllPosts().map((p) => ({ slug: p.slug }));
}
export const dynamicParams = false;

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = getPost((await params).slug);
  return post ? { title: `${post.title} | One Hint Away`, description: post.summary } : {};
}

export default async function PostPage({ params }: Props) {
  const { slug } = await params;
  const post = getPost(slug);
  if (!post) notFound();
  const { prev, next } = getNeighbours(slug);
  const practiceCount = post.practice.length + (post.worked ? 1 : 0);
  // Body = the solutions file: explanation, pseudocode, code tabs, complexity.
  const { default: Body } = await import(`@/content/posts/${post.file}.mdx`);

  return (
    <article className="post">
      {/* 1. Title, pattern, how to recognise it */}
      <header>
        <p className="post-kicker">
          <span className="post-kicker-num">{pad(post.number)}</span>
          <Label>{post.pattern}</Label>
          {post.section !== post.pattern && <span className="post-kicker-section">{post.section}</span>}
        </p>
        <h1 className="chrome">{post.title}</h1>
        <p className="post-summary">{post.summary}</p>
        <ul className="post-meta" aria-label="About this lesson">
          <li>
            <time dateTime={post.published}>{formatDate(post.published)}</time>
          </li>
          <li>{post.slides} slides</li>
          {post.hasCode && <li>Java · Python · C++ · JavaScript</li>}
          {practiceCount > 0 && (
            <li>
              {practiceCount} practice problem{practiceCount > 1 ? "s" : ""}
            </li>
          )}
        </ul>
      </header>

      {/* 2. Slides, with the video slide playing in place */}
      <SlideGallery number={post.number} slides={post.slides} video={post.video} title={post.title} />

      {/* 3–5. Explanation, pseudocode, code tabs, complexity */}
      <div className="post-body">
        <Body />
      </div>

      {/* 6. Practice */}
      {(post.worked || post.practice.length > 0) && (
        <section className="practice">
          <h2>Practice</h2>
          <p className="practice-intro">Try these in order. Open the worked example first if you got stuck on the slides.</p>
          <ul>
            {post.worked && (
              <li>
                <a href={post.worked.url} target="_blank" rel="noopener">
                  {post.worked.name}
                </a>{" "}
                <span className="level">worked example</span>
              </li>
            )}
            {post.practice.map((p) => (
              <li key={p.url}>
                <a href={p.url} target="_blank" rel="noopener">
                  {p.name}
                </a>
                {p.level && <span className={`level level-${p.level}`}>{p.level}</span>}
                {p.note && <p className="practice-note">{p.note}</p>}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* 7. Previous / next in roadmap order */}
      <nav className="post-nav" aria-label="More posts">
        {prev ? (
          <Link href={`/posts/${prev.slug}/`} className="post-nav-prev">
            <span className="post-nav-label">← Previous</span>
            <span className="post-nav-title">
              {pad(prev.number)} · {prev.title}
            </span>
          </Link>
        ) : (
          <span />
        )}
        {next && (
          <Link href={`/posts/${next.slug}/`} className="post-nav-next">
            <span className="post-nav-label">Next →</span>
            <span className="post-nav-title">
              {pad(next.number)} · {next.title}
            </span>
          </Link>
        )}
      </nav>
    </article>
  );
}
