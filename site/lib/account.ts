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
import { ACCOUNTS_ON } from "@/lib/site";

// Not a secret and not the session (that is an HttpOnly cookie scripts can't read):
// only a note that this browser has signed in before, so it is worth asking the API.
const FLAG = "ohw.account";
const TIMEOUT_MS = 8000;

export type SignInLink = { token: string; forDelete: boolean };

type State = {
  ready: boolean; // false until the first check has finished
  email: string | null; // null = signed out (or the API could not be reached)
  done: ReadonlySet<string>;
  link: SignInLink | null; // the token from an emailed link, on /sign-in/ only
};

const SERVER: State = { ready: false, email: null, done: new Set(), link: null };
let state: State = SERVER;
const listeners = new Set<() => void>();
let started = false;

function set(patch: Partial<State>) {
  state = { ...state, ...patch };
  listeners.forEach((fn) => fn());
}

function flag(on: boolean) {
  try {
    if (on) localStorage.setItem(FLAG, "1");
    else localStorage.removeItem(FLAG);
  } catch {
    // private mode: the reader is asked to sign in again on the next page, nothing worse
  }
}

function hasFlag() {
  try {
    return localStorage.getItem(FLAG) === "1";
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
  set({ ready: true, email: null, done: new Set() });
}

async function loadProgress() {
  const res = await call("GET", "/api/v1/progress");
  const done = (res.json as { done?: unknown } | null)?.done;
  if (res.status === 200 && Array.isArray(done)) set({ done: new Set(done as string[]) });
}

// The token arrives after "#" in the emailed link. An inline script on /sign-in/ has
// usually moved it to window.__ohwLink already (see app/sign-in/page.tsx); this also
// reads the address itself, and takes the token out of it either way.
function readLink(): SignInLink | null {
  const w = window as unknown as { __ohwLink?: string };
  const hash = w.__ohwLink ?? window.location.hash;
  delete w.__ohwLink;
  const token = /[#&]token=([A-Za-z0-9_-]{43})(?:&|$)/.exec(hash)?.[1];
  if (window.location.hash.includes("token=")) {
    window.history.replaceState(null, "", window.location.pathname);
  }
  return token ? { token, forDelete: /[#&]for=delete(?:&|$)/.test(hash) } : null;
}

async function start() {
  if (started) return;
  started = true;
  const link = window.location.pathname.startsWith("/sign-in") ? readLink() : null;
  if (!hasFlag()) {
    set({ ready: true, link });
    return;
  }
  set({ link });
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

export type LinkResult = "sent" | "invalid" | "busy" | "down";

function linkResult(status: number): LinkResult {
  return status === 202 ? "sent" : status === 400 ? "invalid" : status === 429 ? "busy" : "down";
}

// Sign in and register are the same request. The API answers the same way whether or
// not the address has an account.
export async function requestLink(email: string): Promise<LinkResult> {
  return linkResult((await call("POST", "/api/v1/auth/link", { email })).status);
}

// The link a signed-in reader needs before deleting the account. It goes to their own address.
export async function requestDeleteLink(): Promise<LinkResult> {
  const { status } = await call("POST", "/api/v1/auth/link", { purpose: "delete" });
  if (status === 401) signedOut();
  return linkResult(status);
}

// The "Sign in" button on the page the emailed link opens. Only this POST uses the token.
export async function spendLink(link: SignInLink): Promise<"in" | "delete" | "gone" | "down"> {
  const res = await call("POST", "/api/v1/auth/session", { token: link.token });
  const body = res.json as { email?: unknown; purpose?: unknown } | null;
  if (res.status === 200 && typeof body?.email === "string") {
    flag(true);
    set({ ready: true, email: body.email, link: null });
    void loadProgress();
    return body.purpose === "delete" ? "delete" : "in";
  }
  if (res.status === 410 || res.status === 400) {
    set({ link: null });
    return "gone";
  }
  return "down";
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
