import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Label } from "@/components/PostList";
import { SlideGallery } from "@/components/SlideGallery";
import { Visualizer } from "@/components/Visualizer";
import { getAllPosts, getNeighbours, getPost } from "@/lib/posts";

type Props = { params: Promise<{ slug: string }> };

const pad = (n: number) => String(n).padStart(2, "0");
const formatDate = (iso: string) =>
  new Date(`${iso}T00:00:00Z`).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });

// Small line icons for the post info chips (decorative: the chip text says it all).
const metaIcons = {
  date: <><rect x="3" y="4.5" width="14" height="12" rx="2" /><path d="M3 8.5h14M7 2.5v4M13 2.5v4" /></>,
  slides: <><path d="M10 3 17 7l-7 4-7-4 7-4Z" /><path d="m3 10.5 7 4 7-4" /></>,
  code: <path d="M7 6 3 10l4 4M13 6l4 4-4 4" />,
  practice: <><circle cx="10" cy="10" r="7" /><circle cx="10" cy="10" r="3.5" /><circle cx="10" cy="10" r="0.6" /></>,
};
function MetaIcon({ name }: { name: keyof typeof metaIcons }) {
  return (
    <svg className="post-meta-icon" viewBox="0 0 20 20" aria-hidden="true" focusable="false">
      {metaIcons[name]}
    </svg>
  );
}

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
            <MetaIcon name="date" />
            <time dateTime={post.published}>{formatDate(post.published)}</time>
          </li>
          <li>
            <MetaIcon name="slides" />
            {post.slides} slides
          </li>
          {post.hasCode && (
            <li>
              <MetaIcon name="code" />
              Java · Python · C++ · JavaScript
            </li>
          )}
          {practiceCount > 0 && (
            <li>
              <MetaIcon name="practice" />
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

      {/* The pattern on the reader's own input (frontmatter: visualizer) */}
      {post.visualizer && (
        <section className="post-body post-visualizer">
          <h2>Try it on your own input</h2>
          <Visualizer pattern={post.visualizer} />
        </section>
      )}

      {/* 6. Practice */}
      {(post.worked || post.practice.length > 0) && (
        <section className="practice">
          <h2>Practice</h2>
          <p className="practice-intro">Try these in order. Open the worked example first if you got stuck on the slides.</p>
          <ul>
            {post.worked && (
              <li>
                <div className="practice-head">
                  <a href={post.worked.url} target="_blank" rel="noopener">
                    {post.worked.name}
                    <span className="practice-arrow" aria-hidden="true">↗</span>
                  </a>
                  <span className="level">worked example</span>
                </div>
              </li>
            )}
            {post.practice.map((p) => (
              <li key={p.url}>
                <div className="practice-head">
                  <a href={p.url} target="_blank" rel="noopener">
                    {p.name}
                    <span className="practice-arrow" aria-hidden="true">↗</span>
                  </a>
                  {p.level && <span className={`level level-${p.level}`}>{p.level}</span>}
                </div>
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
