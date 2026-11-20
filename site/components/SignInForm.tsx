"use client";

import Link from "next/link";
import { useEffect, useId, useState } from "react";
import { useHumanCheck } from "@/components/HumanCheck";
import { type CodeResult, enterCode, requestCode } from "@/lib/account";
import { clearDraft, codeSent, expireIfOld, startOver, typeCode, typeEmail, useSignInDraft } from "@/lib/sign-in-draft";

const SEND_NOTE: Record<Exclude<CodeResult, "sent">, string> = {
  invalid: "That email address doesn't look right.",
  busy: "Too many tries from here. Please try again later.",
  human: "We couldn't confirm you're a person. Please try again.",
  down: "Sign-in is not available right now.",
};

// Before any code is asked for: Cloudflare wants a click, or its check couldn't run at all
// (often a blocker stopping Cloudflare's script).
const HUMAN_NOTE = {
  click: "Tick the box above to show you're a person, then press the button again.",
  failed:
    "We couldn't confirm you're a person. Reload the page and try again. If you use an ad or script blocker, allow challenges.cloudflare.com.",
};

// Sign in, or create an account, in two steps without leaving the page: the reader types
// their email, the API emails a 6-digit code, the reader types the code. Used in the
// header panel and on /sign-in/. Once the code is right, the account store switches every
// open tab to signed in, so this form simply gives way to whatever shows a signed-in reader.
// Which step the reader is on is kept in lib/sign-in-draft.ts, not here, so closing the
// panel and opening it again comes back to the same step (the code step for 15 minutes).
export function SignInForm({ autoFocus = false }: { autoFocus?: boolean }) {
  const id = useId();
  const { email, sentTo, sentAt, code, expired } = useSignInDraft();
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");
  const { boxRef: humanRef, token: humanToken } = useHumanCheck();

  // Back to the email step once the code has run out, also while the form stays open.
  useEffect(() => {
    if (!sentTo) return;
    const left = expireIfOld();
    if (!left) return;
    const timer = window.setTimeout(() => expireIfOld(), left + 500);
    return () => window.clearTimeout(timer);
  }, [sentTo, sentAt]);

  async function sendCode(event: React.FormEvent) {
    event.preventDefault();
    const value = email.trim(); // the API refuses surrounding spaces
    if (!value) return;
    setBusy(true);
    const human = await humanToken();
    if (human.problem) {
      setBusy(false);
      setNote(HUMAN_NOTE[human.problem]);
      return;
    }
    const result = await requestCode(value, human.token);
    setBusy(false);
    if (result === "sent") {
      codeSent(value);
      setNote("");
    } else setNote(SEND_NOTE[result]);
  }

  async function checkCode(event: React.FormEvent) {
    event.preventDefault();
    if (!sentTo || !/^\d{6}$/.test(code)) return;
    setBusy(true);
    const result = await enterCode(sentTo, code);
    setBusy(false);
    if (result === "in" || result === "delete") clearDraft();
    else if (result === "wrong") {
      typeCode("");
      setNote("That code didn't work. Check the newest email, or ask for a new code.");
    } else if (result === "down") setNote("Sign-in is not available right now.");
  }

  function differentEmail() {
    startOver();
    setNote("");
  }

  if (sentTo) {
    return (
      <form className="acct-form" onSubmit={checkCode}>
        <label className="acct-label" htmlFor={`${id}-code`}>
          Code from your email
        </label>
        <p className="acct-small">
          We sent a 6-digit code to <strong>{sentTo}</strong>. It works for 15 minutes.
        </p>
        <input
          id={`${id}-code`}
          className="acct-input acct-code"
          inputMode="numeric"
          autoComplete="one-time-code"
          pattern="[0-9]{6}"
          maxLength={6}
          placeholder="123456"
          required
          autoFocus
          value={code}
          onChange={(e) => typeCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
        />
        <button type="submit" className="acct-submit" disabled={busy || code.length !== 6}>
          {busy ? "Checking" : "Sign in"}
        </button>
        <p className="acct-note" role="status" aria-live="polite">
          {note}
        </p>
        <p className="acct-small">
          No email? Check spam, or{" "}
          <button type="button" className="acct-linkbtn" onClick={differentEmail}>
            use a different email
          </button>
          .
        </p>
      </form>
    );
  }

  return (
    <form className="acct-form" onSubmit={sendCode}>
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
        onChange={(e) => typeEmail(e.target.value)}
      />
      <div ref={humanRef} className="acct-human" />
      <button type="submit" className="acct-submit" disabled={busy}>
        {busy ? "Sending" : "Email me a code"}
      </button>
      <p className="acct-note" role="status" aria-live="polite">
        {note || (expired ? "That code has run out. Ask for a new one." : "")}
      </p>
      <p className="acct-small">
        New here? The code also creates your account. <Link href="/privacy/">What we store</Link>
      </p>
    </form>
  );
}
