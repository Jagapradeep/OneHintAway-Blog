import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { SignedInAs } from "@/components/SignInLink";
import { ACCOUNTS_ON } from "@/lib/site";

// Where a reader lands after pressing "Sign in" on the page the emailed link opened.
export const metadata: Metadata = {
  title: "You're signed in | One Hint Away",
  description: "You are signed in to One Hint Away.",
  robots: { index: false, follow: false },
};

export default function SignedInPage() {
  if (!ACCOUNTS_ON) notFound();
  return (
    <article className="prose acct-page">
      <h1 className="chrome">You&apos;re signed in.</h1>
      <SignedInAs />
      <p>
        Every lesson now has a <strong>Mark as done</strong> button at the end. Finished lessons get a tick on the home
        page and the patterns page, so you can see where you stopped. The button at the top right opens your account:
        sign out, sign out everywhere, or delete it.
      </p>
      <p className="acct-page-actions">
        <Link href="/posts/start-here/" className="button">
          Start here
        </Link>
        <Link href="/patterns/" className="button button-ghost">
          Browse the patterns
        </Link>
      </p>
    </article>
  );
}
