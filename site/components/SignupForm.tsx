"use client";

import { useState } from "react";
import { setNewsletter, useAccount } from "@/lib/account";
import { API_URL } from "@/lib/api";

type State = "idle" | "sending" | "sent" | "invalid" | "busy" | "down";

const NOTE: Record<"invalid" | "busy" | "down", string> = {
  invalid: "That email address doesn't look right.",
  busy: "Too many tries from here. Please try again later.",
  down: "Sign-up is not available right now.",
};

// New patterns by email, in the footer.
// Signed in (accounts on): one button, Subscribe or Unsubscribe, for the reader's own
// address. The sign-in link already proved it is theirs, so there is no email to confirm.
// Signed out: the email field. The API emails a link to confirm (or, for an address that is
// already on the list, a note with an unsubscribe link), and answers the same either way.
export function SignupForm() {
  const { email: account, news } = useAccount();
  if (account) return <OwnAddress email={account} subscribed={news} />;
  return <EmailForm />;
}

// subscribed = null while the reader's status is still loading: the button waits.
function OwnAddress({ email, subscribed }: { email: string; subscribed: boolean | null }) {
  const [busy, setBusy] = useState(false);
  const [failed, setFailed] = useState(false);

  async function change() {
    if (subscribed === null) return;
    setBusy(true);
    setFailed(!(await setNewsletter(!subscribed)));
    setBusy(false);
  }

  return (
    <div className="signup">
      <p className="signup-label">Get new patterns by email</p>
      <p className="signup-status" role="status" aria-live="polite">
        {subscribed ? (
          <>
            You&apos;re subscribed as <strong>{email}</strong>.
          </>
        ) : (
          <>
            One email for each new pattern, to <strong>{email}</strong>. Nothing else.
          </>
        )}
      </p>
      <div className="signup-row">
        <button type="button" className={subscribed ? "signup-off" : undefined} disabled={busy || subscribed === null} onClick={change}>
          {subscribed ? "Unsubscribe" : "Subscribe"}
        </button>
      </div>
      <p className="signup-note">{failed ? "That didn't work. Please try again." : ""}</p>
    </div>
  );
}

function EmailForm() {
  const [email, setEmail] = useState("");
  const [sentTo, setSentTo] = useState("");
  const [state, setState] = useState<State>("idle");

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    const value = email.trim(); // the API refuses surrounding spaces
    if (!value) return;
    setState("sending");
    try {
      const res = await fetch(`${API_URL}/api/v1/subscribers`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: value }),
        signal: AbortSignal.timeout(8000),
      });
      if (res.status === 202) {
        setSentTo(value);
        setState("sent");
      } else setState(res.status === 400 ? "invalid" : res.status === 429 ? "busy" : "down");
    } catch {
      setState("down");
    }
  }

  // Sent: the form is done. One message, nothing more to fill in or press here.
  if (state === "sent") {
    return (
      <div className="signup" role="status">
        <p className="signup-label">Check your inbox</p>
        <p className="signup-status">
          We sent an email to <strong>{sentTo}</strong>. Tap the button in it to finish.
        </p>
      </div>
    );
  }

  return (
    <form className="signup" onSubmit={submit}>
      <label className="signup-label" htmlFor="signup-email">
        Get new patterns by email
      </label>
      <div className="signup-row">
        <input
          id="signup-email"
          type="email"
          name="email"
          autoComplete="email"
          placeholder="you@gmail.com"
          maxLength={254}
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <button type="submit" disabled={state === "sending"}>
          {state === "sending" ? "Sending" : "Subscribe"}
        </button>
      </div>
      <p className="signup-hint">One email for each new pattern. Nothing else. Already subscribed? Enter your email to get an unsubscribe link.</p>
      <p className="signup-note" role="status" aria-live="polite">
        {state === "invalid" || state === "busy" || state === "down" ? NOTE[state] : ""}
      </p>
    </form>
  );
}
