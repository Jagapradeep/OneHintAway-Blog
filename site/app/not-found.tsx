import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "Page not found | One Hint Away" };

// Replaces Next.js's built-in 404, whose own inline styles ignore the site's theme.
// The static export writes this to out/404.html, which Cloudflare Pages serves for unknown URLs.
export default function NotFound() {
  return (
    <section className="hero not-found">
      <p className="post-kicker-num">404</p>
      <h1 className="chrome">This page isn&apos;t here.</h1>
      <p className="lead">The link may be old, or the post may have a new address. Every post is listed on the home page.</p>
      <p>
        <Link href="/" className="button">
          All posts
        </Link>
      </p>
    </section>
  );
}
