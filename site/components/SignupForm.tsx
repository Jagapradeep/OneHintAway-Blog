"use client";

import { useState } from "react";
import { API_URL } from "@/lib/api";

type State = "idle" | "sending" | "sent" | "invalid" | "busy" | "down";

const NOTE: Record<Exclude<State, "idle" | "sending">, string> = {
  sent: "Almost done: open the email we just sent and tap \"Yes, subscribe me\".",
  invalid: "That email address doesn't look right.",
  busy: "Too many tries from here. Please try again later.",
  down: "Sign-up is not available right now.",
};

// Newsletter sign-up. The API stores the address as pending and emails a confirmation
// link (double opt-in); it answers the same way whether or not the address is known.
export function SignupForm() {
  const [email, setEmail] = useState("");
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
        setState("sent");
        setEmail("");
      } else setState(res.status === 400 ? "invalid" : res.status === 429 ? "busy" : "down");
    } catch {
      setState("down");
    }
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
      <p className="signup-hint">One email for each new pattern. Nothing else.</p>
      <p className="signup-note" role="status" aria-live="polite">
        {state !== "idle" && state !== "sending" ? NOTE[state] : ""}
      </p>
    </form>
  );
}
