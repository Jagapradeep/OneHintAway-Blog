"use client";

import { signInStatus, openSignIn, useAccount } from "@/lib/account";
import { canPlay, type Access } from "@/visualizer/access.ts";
import type { Pattern } from "@/visualizer/schema.ts";
import { VisualizerLazy } from "./VisualizerLazy";

// Used only when the site is built with accounts on (components/Visualizer.tsx).
// Signed in: the player. Signed out: the problem, the pseudocode and a card that opens the
// header's sign-in panel; the player and pattern chunks are never fetched. Still checking:
// the same box with the card hidden (the reader may well be signed in), so the height is
// kept and the lock is never shown to someone whose state is unknown. The API down or slow:
// the player (fail open). The rule itself is canPlay() in visualizer/access.ts.
//
// The build renders the "checking" box. Before the page's script runs, CSS shows the card
// at once to a browser that has never signed in (no data-acct on <html>), and its button is
// a plain form to /sign-in/, like the header's.
type Props = {
  patternId: string;
  codeHtml: string;
  tier: Pattern["tier"];
  title: string;
  problem: string;
  blurb: string;
};

export function VisualizerGate({ patternId, codeHtml, tier, title, problem, blurb }: Props) {
  const access: Access = canPlay({ tier }, { accountsOn: true, signIn: signInStatus(useAccount()) });
  if (access === "full" || access === "preview") {
    return <VisualizerLazy patternId={patternId} codeHtml={codeHtml} locked={access === "preview"} />;
  }
  return (
    <div className={`vz-gate${access === "wait" ? " is-wait" : ""}`} role="group" aria-label={`${title} visualizer`}>
      <div className="vz-gate-main">
        <p className="vz-gate-problem">{problem}</p>
        <p className="vz-gate-blurb">{blurb}</p>
        <form
          className="vz-gate-card"
          action="/sign-in/"
          method="get"
          aria-hidden={access === "wait" ? true : undefined}
          onSubmit={(e) => {
            if (openSignIn()) e.preventDefault();
          }}
        >
          <p className="vz-gate-title">Sign in to try it on your own input</p>
          <button type="submit" className="vz-gate-btn" tabIndex={access === "wait" ? -1 : undefined}>
            Sign in
          </button>
        </form>
      </div>
      <div className="vz-gate-code pseudo-block">
        <div className="pseudo-head">{"Pseudocode  ·  any language"}</div>
        <div dangerouslySetInnerHTML={{ __html: codeHtml }} />
      </div>
    </div>
  );
}

// Gallery card lock: a padlock in the card's corner for a signed-out reader (the same mark can
// later stand for a paid pattern). Rendered while checking too, hidden by CSS for a browser that
// has signed in before, so most readers see it from first paint.
export function LockBadge({ tier }: { tier: Pattern["tier"] }) {
  const access = canPlay({ tier }, { accountsOn: true, signIn: signInStatus(useAccount()) });
  if (access !== "sign-in" && access !== "wait") return null;
  return (
    <span className={`vz-gate-lock${access === "wait" ? " is-wait" : ""}`} role="img" aria-label="Locked: sign in to play" title="Sign in to play">
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <rect x="5" y="10.5" width="14" height="10" rx="2.5" />
        <path d="M8.5 10.5V7.5a3.5 3.5 0 0 1 7 0v3" />
      </svg>
    </span>
  );
}
