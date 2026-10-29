import Link from "next/link";
import { getAllPosts } from "@/lib/posts";

// Placeholder home page; step 3 groups posts by roadmap section and adds the theme.
export default function Home() {
  const posts = getAllPosts();
  return (
    <main>
      <h1>One Hint Away</h1>
      <ul>
        {posts.map((p) => (
          <li key={p.slug}>
            <Link href={`/posts/${p.slug}/`}>
              #{String(p.number).padStart(2, "0")} {p.title}
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
