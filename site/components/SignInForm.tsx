"use client";

import Link from "next/link";
import { useId, useState } from "react";
import { type LinkResult, requestLink } from "@/lib/account";
import { API_URL } from "@/lib/api";

const NOTE: Record<LinkResult, string> = {
  sent: "Check your inbox. The link works once and for 15 minutes.",
  invalid: "That email address doesn't look right.",
  busy: "Too many tries from here. Please try again later.",
  down: "Sign-in is not available right now.",
};

// The email field. Signing in and registering are the same thing: the API emails a link,
// and a first sign-in creates the account. Used in the header panel and on /sign-in/.
export function SignInForm() {
  const id = useId();
  const [email, setEmail] = useState("");
  const [news, setNews] = useState(false);
  const [state, setState] = useState<"idle" | "sending" | LinkResult>("idle");
  const [newsSent, setNewsSent] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const value = email.trim(); // the API refuses surrounding spaces
    if (!value) return;
    setState("sending");
    const result = await requestLink(value);
    // The newsletter stays its own list with its own confirmation email (double opt-in).
    if (result === "sent" && news) {
      try {
        const res = await fetch(`${API_URL}/api/v1/subscribers`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: value }),
          signal: AbortSignal.timeout(8000),
        });
        setNewsSent(res.status === 202);
      } catch {
        setNewsSent(false);
      }
    }
    setState(result);
    if (result === "sent") setEmail("");
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
        placeholder="you@example.com"
        maxLength={254}
        required
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <label className="acct-check">
        <input type="checkbox" checked={news} onChange={(e) => setNews(e.target.checked)} />
        <span>Also email me new patterns</span>
      </label>
      <button type="submit" className="acct-submit" disabled={state === "sending"}>
        {state === "sending" ? "Sending" : "Email me a sign-in link"}
      </button>
      <p className="acct-note" role="status" aria-live="polite">
        {state !== "idle" && state !== "sending" ? NOTE[state] : ""}
        {state === "sent" && newsSent ? " A second email asks you to confirm the newsletter." : ""}
      </p>
      <p className="acct-small">
        No password. New here? The same link creates your account. <Link href="/privacy/">What we store</Link>
      </p>
    </form>
  );
}
