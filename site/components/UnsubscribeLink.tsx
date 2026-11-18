"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";

type Step = "working" | "done" | "missing" | "down";

function readToken(): string | null {
  const w = window as unknown as { __ohwUnsub?: string };
  const hash = w.__ohwUnsub ?? window.location.hash;
  if (window.location.hash.includes("token=")) window.history.replaceState(null, "", window.location.pathname);
  return /[#&]token=([A-Za-z0-9_-]{43})(?:&|$)/.exec(hash)?.[1] ?? null;
}

async function unsubscribe(token: string | null): Promise<Step> {
  if (!token) return "missing";
  try {
    const res = await fetch(`${API_URL}/api/v1/subscribers/unsubscribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token }),
      signal: AbortSignal.timeout(8000),
    });
    return res.status === 204 ? "done" : res.status === 400 ? "missing" : "down";
  } catch {
    return "down";
  }
}

// One tap in the email is enough: the page unsubscribes as soon as it opens.
export function UnsubscribeLink() {
  const [step, setStep] = useState<Step>("working");
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const found = readToken();
    void unsubscribe(found).then((result) => {
      setToken(found);
      setStep(result);
    });
  }, []);

  async function retry() {
    setStep("working");
    setStep(await unsubscribe(token));
  }

  if (step === "working") return <p className="lead acct-wait" role="status">One moment.</p>;

  if (step === "down") {
    return (
      <>
        <h1 className="chrome">Couldn&apos;t reach the server.</h1>
        <p className="lead">You are still subscribed. Try again in a moment.</p>
        <p className="subscribed-actions">
          <button type="button" className="button" onClick={retry}>
            Try again
          </button>
        </p>
      </>
    );
  }

  if (step === "missing") {
    return (
      <>
        <h1 className="chrome">That link didn&apos;t work.</h1>
        <p className="lead">It was cut short. Open the email again and tap Unsubscribe.</p>
      </>
    );
  }

  return (
    <>
      <h1 className="chrome">You&apos;re unsubscribed.</h1>
      <p className="lead">Your address is off the list. You won&apos;t get any more emails about new patterns.</p>
      <p>Changed your mind? Subscribe again at the bottom of any page.</p>
      <p className="subscribed-actions">
        <Link href="/" className="button">
          Back to the lessons
        </Link>
      </p>
    </>
  );
}
