"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { SignInForm } from "@/components/SignInForm";
import { deleteAccount, spendLink, useAccount } from "@/lib/account";

type Step = "start" | "working" | "deleting" | "gone" | "down" | "confirm-delete" | "deleted" | "stale";

// The page an emailed link opens. Opening it does nothing: mail scanners and link
// previews open links too. Only the button below sends the token to the API.
export function SignInLink() {
  const { ready, email, link } = useAccount();
  const router = useRouter();
  const [step, setStep] = useState<Step>("start");
  // The link is cleared from the store once used; remember what it was for.
  const [forDelete, setForDelete] = useState(false);

  async function press() {
    if (!link) return;
    setForDelete(link.forDelete);
    setStep("working");
    const result = await spendLink(link);
    if (result === "in") router.replace("/signed-in/");
    else if (result === "delete") setStep("confirm-delete");
    else setStep(result);
  }

  async function reallyDelete() {
    setStep("deleting");
    const result = await deleteAccount();
    setStep(result === "deleted" ? "deleted" : result === "stale" ? "stale" : "confirm-delete");
  }

  if (!ready) return <p className="lead acct-wait">One moment.</p>;

  if (step === "deleted") {
    return (
      <>
        <h1 className="chrome">Your account is deleted.</h1>
        <p className="lead">
          Your email address, your sign-ins and your list of finished lessons are gone. Every lesson stays free to
          read, and you can make a new account any time.
        </p>
        <p className="acct-page-actions">
          <Link href="/" className="button">
            Back to the lessons
          </Link>
        </p>
      </>
    );
  }

  if (step === "confirm-delete" || step === "deleting") {
    return (
      <>
        <h1 className="chrome">Delete your account?</h1>
        <p className="lead">
          This removes {email ?? "your email address"}, your sign-ins on every device and your list of finished
          lessons. It can&apos;t be undone.
        </p>
        <p className="acct-page-actions">
          <button type="button" className="button" disabled={step === "deleting"} onClick={reallyDelete}>
            Delete my account
          </button>
          <Link href="/" className="button button-ghost">
            Keep my account
          </Link>
        </p>
      </>
    );
  }

  if (step === "gone" || step === "stale") {
    return (
      <>
        <h1 className="chrome">That link didn&apos;t work.</h1>
        <p className="lead">
          {step === "stale"
            ? "Too much time has passed since you opened the link. Ask for a new one from the account menu."
            : "A link works once and for 15 minutes. Ask for a new one below."}
        </p>
        {step === "gone" && !email && <SignInForm />}
      </>
    );
  }

  if (link || step === "working" || step === "down") {
    const del = link?.forDelete ?? forDelete;
    return (
      <>
        <h1 className="chrome">{del ? "One more step." : "One click left."}</h1>
        <p className="lead">
          {del
            ? "Press the button to continue. Nothing is deleted until you confirm on the next screen."
            : "Press the button to sign in on this device."}
        </p>
        <p className="acct-page-actions">
          <button type="button" className="button" disabled={step === "working"} onClick={press}>
            {step === "working" ? "One moment" : del ? "Continue" : "Sign in"}
          </button>
        </p>
        <p className="acct-note" role="status" aria-live="polite">
          {step === "down" ? "Could not reach the server. Please try again in a moment." : ""}
        </p>
      </>
    );
  }

  if (email) {
    return (
      <>
        <h1 className="chrome">You&apos;re signed in.</h1>
        <p className="lead">Signed in as {email}.</p>
        <p className="acct-page-actions">
          <Link href="/" className="button">
            Back to the lessons
          </Link>
        </p>
      </>
    );
  }

  return (
    <>
      <h1 className="chrome">Sign in</h1>
      <p className="lead">Enter your email and we&apos;ll send you a link. Keep track of the lessons you have finished.</p>
      <SignInForm />
    </>
  );
}

// On /signed-in/: one line that says who is signed in, or that nobody is.
export function SignedInAs() {
  const { ready, email } = useAccount();
  if (!ready) return <p className="lead acct-wait">One moment.</p>;
  return (
    <p className="lead">
      {email ? `Signed in as ${email} on this device.` : "You are not signed in on this device. Use the Sign in button at the top."}
    </p>
  );
}
