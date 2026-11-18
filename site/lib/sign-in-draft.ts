// Where the reader is in signing in: the email typed so far, and the address a code was
// sent to. It lives here, not in the form, so closing the header panel (a tap outside it,
// Escape, the button again) and opening it later comes back to the same step, and the
// panel and the /sign-in/ page always agree.
//
// Kept for this tab in sessionStorage, so a phone that reloads the page after the reader
// switched to their mail app still asks for the code. A sent code is forgotten after 15
// minutes, when the API stops accepting it anyway. The typed code itself stays in memory only.

import { useSyncExternalStore } from "react";

const KEY = "ohw.signin";
export const CODE_MS = 15 * 60 * 1000; // the API's code lifetime

export type Draft = {
  email: string; // what is in the email field
  sentTo: string | null; // the address the last code went to; null = still on the email step
  sentAt: number; // when that code was sent (ms)
  code: string; // what is in the code field
  expired: boolean; // a code was sent but has run out: say so once on the email step
};

const EMPTY: Draft = { email: "", sentTo: null, sentAt: 0, code: "", expired: false };
let draft: Draft = EMPTY;
let loaded = false;
const listeners = new Set<() => void>();

function load() {
  if (loaded) return;
  loaded = true;
  try {
    const saved = JSON.parse(sessionStorage.getItem(KEY) ?? "null") as Partial<Draft> | null;
    if (saved && typeof saved.email === "string") {
      draft = {
        ...EMPTY,
        email: saved.email,
        sentTo: typeof saved.sentTo === "string" ? saved.sentTo : null,
        sentAt: typeof saved.sentAt === "number" ? saved.sentAt : 0,
      };
    }
  } catch {
    // private mode or a damaged value: start from the email step
  }
}

function save() {
  try {
    if (!draft.email && !draft.sentTo) sessionStorage.removeItem(KEY);
    else sessionStorage.setItem(KEY, JSON.stringify({ email: draft.email, sentTo: draft.sentTo, sentAt: draft.sentAt }));
  } catch {
    // not stored: the step is still kept while the page stays open
  }
}

function set(patch: Partial<Draft>) {
  const persist = "email" in patch || "sentTo" in patch;
  draft = { ...draft, ...patch };
  if (persist) save();
  listeners.forEach((fn) => fn());
}

export function useSignInDraft(): Draft {
  return useSyncExternalStore(
    (fn) => {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    () => {
      load();
      return draft;
    },
    () => EMPTY,
  );
}

export function typeEmail(email: string) {
  set({ email, expired: false });
}

export function typeCode(code: string) {
  set({ code });
}

export function codeSent(email: string) {
  set({ email, sentTo: email, sentAt: Date.now(), code: "", expired: false });
}

// "Use a different email": back to the email step, the address kept for editing.
export function startOver() {
  set({ sentTo: null, sentAt: 0, code: "", expired: false });
}

// Signed in: nothing left to remember.
export function clearDraft() {
  set({ ...EMPTY });
}

// Milliseconds until the sent code runs out; when it already has, go back to the email step.
export function expireIfOld(now = Date.now()): number {
  if (!draft.sentTo) return 0;
  const left = draft.sentAt + CODE_MS - now;
  if (left <= 0) set({ sentTo: null, sentAt: 0, code: "", expired: true });
  return Math.max(left, 0);
}
