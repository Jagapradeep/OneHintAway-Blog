"use client";

import { useState } from "react";
import { setDone, useAccount } from "@/lib/account";

// "Mark as done" on a post. Shows nothing for a signed-out reader or when the API is down.
export function MarkDone({ slug }: { slug: string }) {
  const { email, done } = useAccount();
  const [failed, setFailed] = useState(false);
  if (!email) return null;
  const isDone = done.has(slug);

  async function toggle() {
    setFailed(!(await setDone(slug, !isDone)));
  }

  return (
    <div className="acct-done">
      <button type="button" className={isDone ? "acct-done-btn is-done" : "acct-done-btn"} aria-pressed={isDone} onClick={toggle}>
        <span className="acct-done-box" aria-hidden="true">
          {isDone ? "✓" : ""}
        </span>
        {isDone ? "Done" : "Mark as done"}
      </button>
      <p className="acct-note" role="status" aria-live="polite">
        {failed ? "Could not save that right now." : isDone ? "Saved to your account. Press again to undo." : ""}
      </p>
    </div>
  );
}

// The tick on a post card (home and patterns lists) once the reader has finished that post.
export function DoneTick({ slug }: { slug: string }) {
  const { done } = useAccount();
  if (!done.has(slug)) return null;
  return (
    <span className="acct-tick" role="img" aria-label="Done">
      ✓
    </span>
  );
}
