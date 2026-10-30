import Link from "next/link";
import { Label, PostList } from "@/components/PostList";
import { getPostsBySection } from "@/lib/posts";
import { slugify } from "@/lib/sections";

// Home: every post, grouped by roadmap section in reading order.
export default function Home() {
  const groups = getPostsBySection();
  return (
    <>
      <section className="hero">
        <h1 className="chrome">One pattern at a time.</h1>
        <p className="lead">
          The posts from <strong>@onehintaway</strong>, with the slides, tested code in Java, Python, C++ and
          JavaScript, and problems to practise.
        </p>
        <Link href="/posts/start-here/" className="button">
          Start here
        </Link>
      </section>

      {groups.map(({ section, posts }) => (
        <section key={section} className="roadmap-section" id={slugify(section)}>
          <h2>
            <Label>{section}</Label>
          </h2>
          <PostList posts={posts} />
        </section>
      ))}
    </>
  );
}
