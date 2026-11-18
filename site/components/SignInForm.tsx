"use client";

import Link from "next/link";
import { useId, useState } from "react";
import { type LinkResult, requestLink } from "@/lib/account";

const NOTE: Record<Exclude<LinkResult, "sent">, string> = {
  invalid: "That email address doesn't look right.",
  busy: "Too many tries from here. Please try again later.",
  down: "Sign-in is not available right now.",
};

// The email field. Signing in and registering are the same thing: the API emails a link,
// and a first sign-in creates the account. Used in the header panel and on /sign-in/.
// The newsletter is not offered here: it has its own form in the footer.
export function SignInForm({ autoFocus = false }: { autoFocus?: boolean }) {
  const id = useId();
  const [email, setEmail] = useState("");
  const [sentTo, setSentTo] = useState("");
  const [state, setState] = useState<"idle" | "sending" | LinkResult>("idle");

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const value = email.trim(); // the API refuses surrounding spaces
    if (!value) return;
    setState("sending");
    const result = await requestLink(value);
    setState(result);
    if (result === "sent") setSentTo(value);
  }

  // After sending, the form gives way to one clear next step. If the link is opened in
  // this browser, every open tab switches to signed in by itself (lib/account.ts).
  if (state === "sent") {
    return (
      <div className="acct-sent" role="status">
        <p className="acct-sent-title">Check your inbox</p>
        <p className="acct-lead">
          We sent a sign-in link to <strong>{sentTo}</strong>. Open it in this browser and press <b>Sign in</b>. This
          page updates by itself once you are in.
        </p>
        <p className="acct-small">
          The link works once, for 15 minutes. Nothing after a few minutes? Check your spam folder, or{" "}
          <button type="button" className="acct-linkbtn" onClick={() => setState("idle")}>
            try again
          </button>
          .
        </p>
      </div>
    );
  }

  return (
    <form className="acct-form" onSubmit={submit}>
      <label className="acct-label" htmlFor={`${id}-email`}>
        Your email
      </label>
      <input
        id={`${id}-email`}
        className="acct-input"
        type="email"
        name="email"
        autoComplete="email"
        placeholder="you@gmail.com"
        maxLength={254}
        required
        autoFocus={autoFocus}
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <button type="submit" className="acct-submit" disabled={state === "sending"}>
        {state === "sending" ? "Sending" : "Email me a sign-in link"}
      </button>
      <p className="acct-note" role="status" aria-live="polite">
        {state !== "idle" && state !== "sending" ? NOTE[state] : ""}
      </p>
      <p className="acct-small">
        New here? This link also creates your account. <Link href="/privacy/">What we store</Link>
      </p>
    </form>
  );
}
