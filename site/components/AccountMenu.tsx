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
  setNewsletter,
  signOut,
  useAccount,
} from "@/lib/account";

const DELETE_NOTE: Record<Exclude<CodeResult, "sent">, string> = {
  invalid: "That did not work. Please try again.",
  busy: "Too many tries from here. Please try again later.",
  down: "This is not available right now.",
};

// Header button. Signed out: "Sign in", opening a panel with the email field.
// Signed in: a round badge with the first letter of the reader's email, opening the menu
// (sign out, sign out everywhere, delete). While the API is still being asked (a reader who
// has signed in before), it shows the plain icon and the panel says so: never "Sign in".
// The button sits in a plain form that opens /sign-in/, so a tap that lands before the
// page's script has loaded still goes somewhere useful; once loaded, it opens the panel.
// Only rendered when the site was built with accounts on (see app/layout.tsx).
export function AccountMenu() {
  const { ready, email, done, news } = useAccount();
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

  async function switchNews() {
    if (news === null) return;
    setBusy(true);
    const ok = await setNewsletter(!news);
    setBusy(false);
    setNote(ok ? (news ? "Done. No more emails." : "Done. You'll get an email for each new pattern.") : "That didn't work. Please try again.");
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
              <p className="acct-title">Your account</p>
              <p className="acct-email">{email}</p>
              <p className="acct-lead">
                {done.size} {done.size === 1 ? "lesson" : "lessons"} done
              </p>
              <div className="acct-actions">
                <button type="button" disabled={busy || news === null} onClick={switchNews}>
                  {news ? "Stop new-pattern emails" : "Email me new patterns"}
                </button>
                <button type="button" disabled={busy} onClick={() => leave(false)}>
                  Sign out
                </button>
                <button type="button" disabled={busy} onClick={() => leave(true)}>
                  Sign out everywhere
                </button>
                <button type="button" disabled={busy} onClick={() => (setView("delete"), setNote(""))}>
                  Delete account
                </button>
              </div>
              <p className="acct-note" role="status" aria-live="polite">
                {note}
              </p>
              <p className="acct-small">
                <Link href="/privacy/" onClick={() => setOpen(false)}>
                  What we store
                </Link>
              </p>
            </>
          )}
          {email && view !== "menu" && (
            <>
              <p className="acct-title">Delete your account</p>
              {view === "delete" && (
                <>
                  <p className="acct-lead">
                    This removes your email address, your sign-ins on every device and your list of finished lessons.
                    To make sure it is you, we first email a code to {email}.
                  </p>
                  <div className="acct-actions">
                    <button type="button" disabled={busy} onClick={askDeleteCode}>
                      Email me a code
                    </button>
                    <button type="button" disabled={busy} onClick={() => (setView("menu"), setNote(""))}>
                      Keep my account
                    </button>
                  </div>
                </>
              )}
              {view === "code" && (
                <form className="acct-form" onSubmit={checkDeleteCode}>
                  <label className="acct-label" htmlFor={codeId}>
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
                  <button type="submit" className="acct-submit" disabled={busy || code.length !== 6}>
                    Continue
                  </button>
                  <p className="acct-small">
                    <button type="button" className="acct-linkbtn" disabled={busy} onClick={() => (setView("menu"), setCode(""), setNote(""))}>
                      Keep my account
                    </button>
                  </p>
                </form>
              )}
              {view === "confirm" && (
                <>
                  <p className="acct-lead">This can&apos;t be undone.</p>
                  <div className="acct-actions">
                    <button type="button" disabled={busy} onClick={reallyDelete}>
                      Delete my account
                    </button>
                    <button type="button" disabled={busy} onClick={() => (setView("menu"), setNote(""))}>
                      Keep my account
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
