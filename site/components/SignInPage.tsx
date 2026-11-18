"use client";

import Link from "next/link";
import { SignInForm } from "@/components/SignInForm";
import { useAccount } from "@/lib/account";

// /sign-in/: the same two steps as the header panel, on a page of their own (the header
// button opens it when tapped before the page's script has loaded).
export function SignInPage() {
  const { ready, email } = useAccount();
  if (!ready) return <p className="lead acct-wait">One moment.</p>;

  if (email) {
    return (
      <>
        <h1 className="chrome">You&apos;re signed in.</h1>
        <p className="lead">Signed in as {email} on this device.</p>
        <p>
          Every lesson has a <strong>Mark as done</strong> button at the end. Finished lessons get a tick on the home
          page and the patterns page, so you can see where you stopped. The button at the top right opens your
          account.
        </p>
        <p className="acct-page-actions">
          <Link href="/posts/start-here/" className="button">
            Start here
          </Link>
          <Link href="/patterns/" className="button button-ghost">
            Browse the patterns
          </Link>
        </p>
      </>
    );
  }

  return (
    <>
      <h1 className="chrome">Sign in</h1>
      <p className="lead">We&apos;ll email you a code. Keep track of the lessons you have finished.</p>
      <SignInForm autoFocus />
    </>
  );
}
