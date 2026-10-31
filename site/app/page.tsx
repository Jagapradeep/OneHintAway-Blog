import Link from "next/link";
import { HeroArt } from "@/components/HeroArt";
import { PostList } from "@/components/PostList";
import { getPostsBySection, getSiteStats } from "@/lib/posts";
import { SECTIONS, pad2, sectionIndex, slugify } from "@/lib/sections";
import { INSTAGRAM_URL } from "@/lib/site";

const STEPS = [
  {
    title: "Spot the clue",
    text: "Every pattern leaves a clue in the problem statement. Learn the words that give it away.",
  },
  {
    title: "Watch it run",
    text: "A dry run on a tiny input, step by step on the slides, so you see why it works.",
  },
  {
    title: "Code it your way",
    text: "Pseudocode first, then tested code in Java, Python, C++ and JavaScript.",
  },
  {
    title: "Practise",
    text: "Hand-picked LeetCode problems, easiest first, each with a one-line hint.",
  },
];

// Home: what the site is, how a lesson works, the roadmap, then every lesson by section.
export default function Home() {
  const groups = getPostsBySection();
  const stats = getSiteStats();
  const counts = new Map(groups.map((g) => [g.section.toLowerCase(), g.posts.length]));

  return (
    <div className="page-wide">
      <section className="hero" aria-labelledby="hero-title">
        <div className="hero-text">
          <p className="eyebrow">Free DSA course · beginner friendly</p>
          <h1 id="hero-title" className="chrome">
            Learn DSA by spotting the <span className="gold-text">pattern</span>.
          </h1>
          <p className="lead">
            Most coding interview problems are a few dozen patterns in disguise. One Hint Away teaches data structures
            and algorithms one pattern at a time, in order: the clue that gives it away, a dry run you can follow, and
            code in four languages.
          </p>
          <div className="hero-actions">
            <Link href="/posts/start-here/" className="button">
              Start learning →
            </Link>
            <Link href="/patterns/" className="button button-ghost">
              Browse patterns
            </Link>
          </div>
          <dl className="stats">
            <div>
              <dt>Lessons</dt>
              <dd>{stats.posts}</dd>
            </div>
            <div>
              <dt>Patterns</dt>
              <dd>{stats.patterns}</dd>
            </div>
            <div>
              <dt>Practice problems</dt>
              <dd>{stats.problems}</dd>
            </div>
            <div>
              <dt>Languages</dt>
              <dd>4</dd>
            </div>
          </dl>
        </div>
        <div className="hero-visual">
          <HeroArt />
        </div>
      </section>

      <section className="home-block" aria-labelledby="how-title">
        <p className="eyebrow">How every lesson works</p>
        <h2 id="how-title">From “I’ve never seen this” to solved, in four steps.</h2>
        <ol className="steps">
          {STEPS.map((s, i) => (
            <li key={s.title} className="step">
              <span className="step-num">{pad2(i + 1)}</span>
              <h3>{s.title}</h3>
              <p>{s.text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="home-block" aria-labelledby="roadmap-title">
        <p className="eyebrow">The roadmap</p>
        <h2 id="roadmap-title">One path from zero to interview ready.</h2>
        <p className="block-lead">
          Follow the sections in order, or jump to the one you need. New lessons land every few days on{" "}
          <a href={INSTAGRAM_URL} target="_blank" rel="noopener">
            @onehintaway
          </a>
          .
        </p>
        <ol className="roadmap">
          {SECTIONS.map((section, i) => {
            const n = counts.get(section.toLowerCase()) ?? 0;
            const inner = (
              <>
                <span className="roadmap-num">{pad2(i)}</span>
                <span className="roadmap-name">{section}</span>
                <span className="roadmap-count">{n ? `${n} lesson${n > 1 ? "s" : ""}` : "Coming soon"}</span>
              </>
            );
            return (
              <li key={section}>
                {n ? (
                  <a href={`#${slugify(section)}`} className="roadmap-tile is-live">
                    {inner}
                  </a>
                ) : (
                  <span className="roadmap-tile">{inner}</span>
                )}
              </li>
            );
          })}
        </ol>
      </section>

      <section className="home-block" aria-labelledby="lessons-title">
        <p className="eyebrow">All lessons</p>
        <h2 id="lessons-title">Every lesson, in reading order.</h2>
        {groups.map(({ section, posts }) => (
          <section key={section} className="roadmap-section" id={slugify(section)} aria-label={section}>
            <div className="section-head">
              <span className="section-index">{pad2(sectionIndex(section))}</span>
              <h3>{section}</h3>
              <span className="section-count">
                {posts.length} lesson{posts.length > 1 ? "s" : ""}
              </span>
            </div>
            <PostList posts={posts} grid />
          </section>
        ))}
      </section>

      <section className="cta-band" aria-label="Follow One Hint Away">
        <div>
          <h2>One new pattern every few days.</h2>
          <p>Follow @onehintaway on Instagram for the slides as they come out, then come back here for the code.</p>
        </div>
        <a href={INSTAGRAM_URL} target="_blank" rel="noopener" className="button">
          Follow on Instagram
        </a>
      </section>
    </div>
  );
}
