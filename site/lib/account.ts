// Reader accounts: who is signed in, and which lessons they marked as done.
//
// One small store shared by every component on the page (the header menu, the done ticks,
// the "Mark as done" button). Like everything that talks to the API, it must never break
// a page: every call returns a plain result, never throws, and a failing or missing API
// simply leaves the reader looking signed out.
//
// A reader who has never signed in on this browser makes no account request at all: the
// store only asks the API "who am I?" when the flag below is present.

import { useEffect, useSyncExternalStore } from "react";
import { API_URL } from "@/lib/api";
import { ACCOUNT_FLAG, ACCOUNTS_ON } from "@/lib/site";

// Not a secret and not the session (that is an HttpOnly cookie scripts can't read):
// only a note that this browser has signed in before, so it is worth asking the API.
// Its value is the time of the last sign-in or sign-out, so every change reaches the
// other open tabs as a "storage" event (they then update their header too).
// app/layout.tsx reads it before the page paints (ACCOUNT_SCRIPT in lib/site.ts).
const FLAG = ACCOUNT_FLAG;
const TIMEOUT_MS = 8000;

type State = {
  ready: boolean; // false until the first check has finished
  email: string | null; // null = signed out (or the API could not be reached)
  done: ReadonlySet<string>;
  news: boolean | null; // on the newsletter list? null = not known (signed out, or not loaded yet)
};

const SERVER: State = { ready: false, email: null, done: new Set(), news: null };
let state: State = SERVER;
const listeners = new Set<() => void>();
let started = false;

function set(patch: Partial<State>) {
  state = { ...state, ...patch };
  listeners.forEach((fn) => fn());
}

function flag(on: boolean) {
  try {
    if (on) localStorage.setItem(FLAG, String(Date.now()));
    else localStorage.removeItem(FLAG);
  } catch {
    // private mode: the reader is asked to sign in again on the next page, nothing worse
  }
}

function hasFlag() {
  try {
    return localStorage.getItem(FLAG) !== null;
  } catch {
    return false;
  }
}

// Every account call: the cookie goes along (credentials), and the custom header is what
// the API's CSRF check asks for. Returns the HTTP status, or 0 when the API is unreachable.
async function call(method: string, path: string, body?: unknown): Promise<{ status: number; json: unknown }> {
  try {
    const res = await fetch(API_URL + path, {
      method,
      credentials: "include",
      headers: body === undefined ? { "X-OHW-CSRF": "1" } : { "X-OHW-CSRF": "1", "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    let json: unknown = null;
    if (res.ok && res.status !== 204 && res.status !== 202) json = await res.json().catch(() => null);
    return { status: res.status, json };
  } catch {
    return { status: 0, json: null };
  }
}

function signedOut() {
  flag(false);
  set({ ready: true, email: null, done: new Set(), news: null });
}

// After signing in: the finished lessons and whether the reader gets new patterns by email.
async function loadProgress() {
  const [res, news] = await Promise.all([call("GET", "/api/v1/progress"), call("GET", "/api/v1/subscribers/me")]);
  const done = (res.json as { done?: unknown } | null)?.done;
  if (res.status === 200 && Array.isArray(done)) set({ done: new Set(done as string[]) });
  const subscribed = (news.json as { subscribed?: unknown } | null)?.subscribed;
  if (news.status === 200 && typeof subscribed === "boolean") set({ news: subscribed });
}

// Another tab signed in or out: the cookie is shared, so follow it here.
function onStorage(event: StorageEvent) {
  if (event.key !== FLAG && event.key !== null) return;
  if (hasFlag()) void check();
  else set({ ready: true, email: null, done: new Set(), news: null });
}

async function start() {
  if (started) return;
  started = true;
  window.addEventListener("storage", onStorage);
  if (!hasFlag()) {
    set({ ready: true });
    return;
  }
  await check();
}

async function check() {
  const me = await call("GET", "/api/v1/auth/me");
  const email = (me.json as { email?: unknown } | null)?.email;
  if (me.status === 200 && typeof email === "string") {
    set({ ready: true, email });
    void loadProgress();
  } else if (me.status === 401) {
    signedOut();
  } else {
    // API down or slow: look signed out for now, and ask again on the next page.
    set({ ready: true });
  }
}

export function useAccount(): State {
  const snapshot = useSyncExternalStore(
    (fn) => {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    () => state,
    () => SERVER,
  );
  useEffect(() => {
    if (ACCOUNTS_ON && API_URL) void start();
  }, []);
  return snapshot;
}

export type CodeResult = "sent" | "invalid" | "busy" | "down";

function codeResult(status: number): CodeResult {
  return status === 202 ? "sent" : status === 400 ? "invalid" : status === 429 ? "busy" : "down";
}

// Sign in and register are the same request: the API emails a 6-digit code. It answers
// the same way whether or not the address has an account.
export async function requestCode(email: string): Promise<CodeResult> {
  return codeResult((await call("POST", "/api/v1/auth/code", { email })).status);
}

// The code a signed-in reader needs before deleting the account. It goes to their own address.
export async function requestDeleteCode(): Promise<CodeResult> {
  const { status } = await call("POST", "/api/v1/auth/code", { purpose: "delete" });
  if (status === 401) signedOut();
  return codeResult(status);
}

// The reader types the code from the email. "wrong" covers wrong, expired and used codes
// (the API does not say which); a code dies after five wrong tries.
export async function enterCode(email: string, code: string): Promise<"in" | "delete" | "wrong" | "down"> {
  const res = await call("POST", "/api/v1/auth/session", { email, code });
  const body = res.json as { email?: unknown; purpose?: unknown } | null;
  if (res.status === 200 && typeof body?.email === "string") {
    flag(true);
    set({ ready: true, email: body.email });
    void loadProgress();
    return body.purpose === "delete" ? "delete" : "in";
  }
  return res.status === 410 || res.status === 400 ? "wrong" : "down";
}

export async function signOut(everywhere = false): Promise<boolean> {
  const { status } = await call("POST", everywhere ? "/api/v1/auth/sign-out-everywhere" : "/api/v1/auth/sign-out");
  if (status === 204 || status === 401) {
    signedOut();
    return true;
  }
  return false;
}

// "stale" = the API wants a fresh emailed link first.
export async function deleteAccount(): Promise<"deleted" | "stale" | "down"> {
  const { status } = await call("DELETE", "/api/v1/auth/account");
  if (status === 204) {
    signedOut();
    return "deleted";
  }
  if (status === 401) signedOut();
  return status === 403 || status === 401 ? "stale" : "down";
}

// New patterns by email, for a signed-in reader: one click, no confirmation email (the
// sign-in link already proved the address). Shown at once, taken back if not saved.
export async function setNewsletter(on: boolean): Promise<boolean> {
  const before = state.news;
  set({ news: on });
  const { status } = await call(on ? "PUT" : "DELETE", "/api/v1/subscribers/me");
  if (status === 204) return true;
  if (status === 401) signedOut();
  else set({ news: before });
  return false;
}

// Shows the change at once and takes it back if the API did not save it.
export async function setDone(slug: string, done: boolean): Promise<boolean> {
  const before = state.done;
  const next = new Set(before);
  if (done) next.add(slug);
  else next.delete(slug);
  set({ done: next });
  const { status } = await call(done ? "PUT" : "DELETE", `/api/v1/progress/${slug}`);
  if (status === 204) return true;
  if (status === 401) signedOut();
  else set({ done: before });
  return false;
}
