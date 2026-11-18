// Who may play a pattern: free and paid tiers, and (when accounts are on) sign-in.
//
// PAYWALL_ON is off until there is a login, a payment and a server check.
// While it is off, every pattern is fully open. Turning it on makes a paid
// pattern a preview: it plays the post's example, without the reader's own
// input. That alone is a courtesy lock, not protection: the code still reaches
// every browser. Real protection means serving paid chunks (loaders.ts) only
// after a server has checked the reader's access.
//
// Sign-in gate: with accounts on, the player plays only for a signed-in reader
// (every pattern, free and paid). It is a reason to sign up, not protection: the
// chunks are static files anyone can fetch. It fails open: a reader whose state
// is unknown (the API is down or slow) gets the player.
import type { Pattern } from "./schema.ts";

export const PAYWALL_ON = false;

export function isLocked(p: Pick<Pattern, "tier">): boolean {
  return PAYWALL_ON && p.tier === "paid";
}

// "checking" = still asking the API; "unknown" = the API could not be reached.
export type SignIn = "in" | "out" | "checking" | "unknown";

// full = the player with the reader's own input; preview = the post's example only (paywall);
// sign-in = show the sign-in card instead of the player; wait = keep the space, show neither.
export type Access = "full" | "preview" | "sign-in" | "wait";

export function canPlay(p: Pick<Pattern, "tier">, account: { accountsOn: boolean; signIn: SignIn }): Access {
  if (account.accountsOn) {
    if (account.signIn === "checking") return "wait";
    if (account.signIn === "out") return "sign-in";
  }
  return isLocked(p) ? "preview" : "full";
}
