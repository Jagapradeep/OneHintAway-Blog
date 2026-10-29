import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getAllPosts, getPost } from "@/lib/posts";

type Props = { params: Promise<{ slug: string }> };

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
  const post = getPost((await params).slug);
  if (!post) notFound();
  const { default: Body } = await import(`@/content/posts/${post.file}.mdx`);

  return (
    <article>
      <p>#{String(post.number).padStart(2, "0")} · {post.pattern}</p>
      <h1>{post.title}</h1>
      <p>{post.summary}</p>
      <Body />
    </article>
  );
}
