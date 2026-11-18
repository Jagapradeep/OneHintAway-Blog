import type { Metadata } from "next";
import Link from "next/link";

// Where the API sends a reader who opened a good confirmation link.
export const metadata: Metadata = {
  title: "You're subscribed | One Hint Away",
  description: "Your email is confirmed.",
  robots: { index: false, follow: false },
};

export default function SubscribedPage() {
  return (
    <article className="prose subscribed">
      <h1 className="chrome">You&apos;re subscribed.</h1>
      <p className="lead">We&apos;ll email you each time a new pattern is posted.</p>

      <div className="subscribed-promise">
        <p className="subscribed-promise-head">WHAT YOU GET</p>
        <p>
          <b>for each</b> new pattern: one email
          <br />
          <b>never</b>: ads, other lists, or your address shared
        </p>
      </div>

      <p>No need to wait for the first one: everything on the site is already free to read.</p>
      <p className="subscribed-actions">
        <Link href="/posts/start-here/" className="button">
          Start here
        </Link>
        <Link href="/patterns/" className="button button-ghost">
          Browse the patterns
        </Link>
        <Link href="/visualize/" className="button button-ghost">
          Step through one yourself
        </Link>
      </p>
    </article>
  );
}
