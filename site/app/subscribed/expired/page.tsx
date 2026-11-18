import type { Metadata } from "next";
import Link from "next/link";

// Where the API sends a reader whose confirmation link it did not recognise.
export const metadata: Metadata = {
  title: "That link didn't work | One Hint Away",
  description: "The confirmation link was not recognised.",
  robots: { index: false, follow: false },
};

export default function ExpiredPage() {
  return (
    <article className="prose subscribed">
      <h1 className="chrome">That link didn&apos;t work.</h1>
      <p className="lead">You&apos;re not subscribed yet.</p>
      <p>The link was cut short or is not one we sent. Mail apps sometimes split long links in two.</p>
      <ul>
        <li>Open the email again and tap the button, or</li>
        <li>enter your email once more at the bottom of any page, and we&apos;ll send a fresh link.</li>
      </ul>
      <p className="subscribed-actions">
        <Link href="/" className="button">
          Back to the site
        </Link>
      </p>
    </article>
  );
}
