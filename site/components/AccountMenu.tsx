"use client";

import Link from "next/link";
import { useEffect, useId, useRef, useState } from "react";
import { SignInForm } from "@/components/SignInForm";
import {
  type CodeResult,
  deleteAccount,
  enterCode,
  onOpenSignIn,
  requestDeleteCode,
  signOut,
  useAccount,
} from "@/lib/account";

const DELETE_NOTE: Record<Exclude<CodeResult, "sent">, string> = {
  invalid: "That did not work. Please try again.",
  busy: "Too many tries from here. Please try again later.",
  human: "That did not work. Please try again.", // not asked for this code: it needs a session
  down: "This is not available right now.",
};

// Header button. Signed out: "Sign in", opening a panel with the email field.
// Signed in: a round badge with the first letter of the reader's email, opening the menu
// (who is signed in, progress, sign out, sign out everywhere, delete). The newsletter switch
// lives in the footer only. While the API is still being asked (a reader who
// has signed in before), it shows the plain icon and the panel says so: never "Sign in".
// The button sits in a plain form that opens /sign-in/, so a tap that lands before the
// page's script has loaded still goes somewhere useful; once loaded, it opens the panel.
// Only rendered when the site was built with accounts on (see app/layout.tsx).
export function AccountMenu({ total }: { total: number }) {
  const { ready, email, done } = useAccount();
  const doneCount = Math.min(done.size, total);
  const percent = total ? Math.round((doneCount / total) * 100) : 0;
  const status = email ? "in" : ready ? "out" : "checking";
  const [open, setOpen] = useState(false);
  // Deleting: "delete" asks for a code, "code" takes it, "confirm" asks once more. Closing
  // the panel keeps the step (like the sign-in steps); a different reader starts at the menu.
  const [view, setView] = useState<"menu" | "delete" | "code" | "confirm">("menu");
  const [code, setCode] = useState("");
  const [viewFor, setViewFor] = useState(email);
  if (viewFor !== email) {
    setViewFor(email);
    setView("menu");
    setCode("");
  }
  const codeId = useId();
  const [note, setNote] = useState("");
  const [busy, setBusy] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);
  // Opened from elsewhere on the page (the visualizer's sign-in card): close again once the
  // reader is signed in, so the panel does not cover what just unlocked.
  const fromPage = useRef(false);

  useEffect(
    () =>
      onOpenSignIn(() => {
        fromPage.current = true;
        setOpen(true);
        setNote("");
      }),
    [],
  );

  useEffect(() => {
    if (email && fromPage.current) {
      fromPage.current = false;
      setOpen(false);
    }
  }, [email]);

  // Close on Escape or a click outside.
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    const onDown = (e: PointerEvent) => !rootRef.current?.contains(e.target as Node) && setOpen(false);
    document.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onDown);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("pointerdown", onDown);
    };
  }, [open]);

  // Opening again returns to where the reader was (see SignInForm and the delete steps).
  function toggle() {
    fromPage.current = false;
    setOpen((o) => !o);
    setNote("");
  }

  async function leave(everywhere: boolean) {
    setBusy(true);
    const ok = await signOut(everywhere);
    setBusy(false);
    if (ok) setOpen(false);
    else setNote("Could not sign out right now. Please try again.");
  }

  function toMenu() {
    setView("menu");
    setCode("");
    setNote("");
  }

  async function askDeleteCode() {
    setBusy(true);
    const result = await requestDeleteCode();
    setBusy(false);
    if (result === "sent") {
      setView("code");
      setNote("");
    } else setNote(DELETE_NOTE[result]);
  }

  async function checkDeleteCode(event: React.FormEvent) {
    event.preventDefault();
    if (!email || !/^\d{6}$/.test(code)) return;
    setBusy(true);
    const result = await enterCode(email, code);
    setBusy(false);
    setCode("");
    if (result === "delete") {
      setView("confirm");
      setNote("");
    } else setNote(result === "down" ? "This is not available right now." : "That code didn't work. Please try again.");
  }

  async function reallyDelete() {
    setBusy(true);
    const result = await deleteAccount();
    setBusy(false);
    if (result === "deleted") setOpen(false);
    else setNote(result === "stale" ? "Too much time has passed. Ask for a new code." : "This is not available right now.");
  }

  return (
    <div className="acct" ref={rootRef}>
      <form
        className="acct-open"
        action="/sign-in/"
        method="get"
        onSubmit={(e) => {
          e.preventDefault();
          toggle();
        }}
      >
        <button
          type="submit"
          className={`acct-btn is-${status}`}
          aria-label={status === "in" ? "Your account" : status === "out" ? "Sign in" : "Account"}
          aria-expanded={open}
          aria-controls="acct-panel"
        >
          {email ? (
            <span className="acct-avatar" aria-hidden="true">
              {email.charAt(0).toUpperCase()}
            </span>
          ) : (
            <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
              <circle cx="12" cy="8.5" r="3.6" />
              <path d="M4.8 20c.9-3.6 3.7-5.4 7.2-5.4s6.3 1.8 7.2 5.4" />
            </svg>
          )}
          {!email && <span className="acct-btn-text">Sign in</span>}
        </button>
      </form>
      {open && (
        <div className="acct-panel" id="acct-panel">
          {status === "checking" && (
            <>
              <p className="acct-title">Your account</p>
              <p className="acct-lead acct-wait">Checking whether you are signed in.</p>
            </>
          )}
          {status === "out" && (
            <>
              <p className="acct-title">Sign in</p>
              <p className="acct-lead">Keep track of the lessons you have finished.</p>
              <SignInForm autoFocus />
            </>
          )}
          {email && view === "menu" && (
            <>
              <div className="acct-who">
                <span className="acct-who-badge" aria-hidden="true">
                  {email.charAt(0).toUpperCase()}
                </span>
                <div className="acct-who-text">
                  <p className="acct-who-label">Signed in as</p>
                  <p className="acct-who-email" title={email}>
                    {email}
                  </p>
                </div>
              </div>
              <div className="acct-progress">
                <p className="acct-progress-row">
                  <span className="acct-progress-label">Your progress</span>
                  <span className="acct-progress-count">
                    <strong>{doneCount}</strong> of {total} lessons
                  </span>
                </p>
                <div className="acct-bar" aria-hidden="true">
                  <span style={{ width: `${percent}%` }} />
                </div>
                {doneCount === 0 && (
                  <p className="acct-progress-hint">Tap &ldquo;Mark as done&rdquo; at the end of a post to fill this bar.</p>
                )}
              </div>
              <div className="acct-items">
                <button type="button" className="acct-item" disabled={busy} onClick={() => leave(false)}>
                  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                    <path d="M14 4h4a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-4" />
                    <path d="M10 8l-4 4 4 4M6 12h9" />
                  </svg>
                  <span className="acct-item-text">
                    <span className="acct-item-label">Sign out</span>
                    <span className="acct-item-hint">On this device only</span>
                  </span>
                </button>
                <button type="button" className="acct-item" disabled={busy} onClick={() => leave(true)}>
                  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                    <rect x="3" y="4" width="13" height="10" rx="1.5" />
                    <path d="M7 18h5M9.5 14v4" />
                    <rect x="17" y="9" width="4.5" height="10" rx="1" />
                  </svg>
                  <span className="acct-item-text">
                    <span className="acct-item-label">Sign out everywhere</span>
                    <span className="acct-item-hint">Every phone and laptop, this one too</span>
                  </span>
                </button>
                <button type="button" className="acct-item is-danger" disabled={busy} onClick={() => (setView("delete"), setNote(""))}>
                  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                    <path d="M4 7h16M9 7V4.5h6V7M6.5 7l1 12.5h9l1-12.5M10 11v5M14 11v5" />
                  </svg>
                  <span className="acct-item-text">
                    <span className="acct-item-label">Delete account</span>
                    <span className="acct-item-hint">Removes your email and progress</span>
                  </span>
                </button>
              </div>
              <p className="acct-note acct-menu-note" role="status" aria-live="polite">
                {note}
              </p>
              <p className="acct-foot">
                <Link href="/privacy/" onClick={() => setOpen(false)}>
                  What we store about you
                </Link>
              </p>
            </>
          )}
          {email && view !== "menu" && (
            <>
              <div className="acct-head">
                <button type="button" className="acct-back" aria-label="Back to your account" disabled={busy} onClick={toMenu}>
                  <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                    <path d="M15 5l-7 7 7 7" />
                  </svg>
                </button>
                <p className="acct-title">Delete your account</p>
              </div>
              {view === "delete" && (
                <>
                  <p className="acct-lead">This removes:</p>
                  <ul className="acct-gone">
                    <li>your email address</li>
                    <li>your list of finished lessons</li>
                    <li>your sign-ins on every device</li>
                  </ul>
                  <p className="acct-lead">
                    To make sure it is you, we first email a 6-digit code to <strong className="acct-strong">{email}</strong>.
                  </p>
                  <div className="acct-btns">
                    <button type="button" className="acct-btn2" disabled={busy} onClick={toMenu}>
                      Keep my account
                    </button>
                    <button type="button" className="acct-btn2 is-danger" disabled={busy} onClick={askDeleteCode}>
                      Email me a code
                    </button>
                  </div>
                </>
              )}
              {view === "code" && (
                <form className="acct-form" onSubmit={checkDeleteCode}>
                  <p className="acct-lead acct-lead-flush">
                    We sent a code to <strong className="acct-strong">{email}</strong>.
                  </p>
                  <label className="acct-label acct-label-gap" htmlFor={codeId}>
                    Code from your email
                  </label>
                  <input
                    id={codeId}
                    className="acct-input acct-code"
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    pattern="[0-9]{6}"
                    maxLength={6}
                    placeholder="123456"
                    required
                    autoFocus
                    value={code}
                    onChange={(e) => setCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
                  />
                  <div className="acct-btns">
                    <button type="button" className="acct-btn2" disabled={busy} onClick={toMenu}>
                      Keep my account
                    </button>
                    <button type="submit" className="acct-btn2 is-danger" disabled={busy || code.length !== 6}>
                      Continue
                    </button>
                  </div>
                </form>
              )}
              {view === "confirm" && (
                <>
                  <div className="acct-warn">
                    <strong>Last step.</strong> This can&apos;t be undone: your progress is gone for good.
                  </div>
                  <div className="acct-btns">
                    <button type="button" className="acct-btn2" disabled={busy} onClick={toMenu}>
                      Keep my account
                    </button>
                    <button type="button" className="acct-btn2 is-danger is-fill" disabled={busy} onClick={reallyDelete}>
                      Delete my account
                    </button>
                  </div>
                </>
              )}
              <p className="acct-note" role="status" aria-live="polite">
                {note}
              </p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
