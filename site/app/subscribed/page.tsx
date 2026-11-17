import type { Metadata } from "next";
import Link from "next/link";
import { ConfirmSteps } from "@/components/ConfirmSteps";

// Where the API sends a reader who opened a good confirmation link.
export const metadata: Metadata = {
  title: "You're in | One Hint Away",
  description: "Your email is confirmed.",
  robots: { index: false, follow: false },
};

export default function SubscribedPage() {
  return (
    <article className="prose subscribed">
      <h1 className="chrome">You&apos;re in.</h1>
      <p className="lead">Your email is confirmed. You&apos;re subscribed.</p>

      <ConfirmSteps at={2} />

      <p>
        New patterns will reach your inbox as they are published, and nothing else will. There is no need to wait
        for the first one: everything already on the site is free to read.
      </p>
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
