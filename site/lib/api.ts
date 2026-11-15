// The site's link to the Spring Boot API (view counts, copy counts, search).
//
// The site must never depend on the API: every post is a static page that works alone.
// So the address is fixed at build time, and an empty address switches every extra off.
// It is empty in production until the API has a server (Phase 5). Every call below
// returns null instead of throwing, so a slow, failing or missing API shows nothing.

export const API_URL = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/+$/, "");

const TIMEOUT_MS = 4000;

export async function apiGet<T>(path: string, signal?: AbortSignal): Promise<T | null> {
  if (!API_URL) return null;
  try {
    const timeout = AbortSignal.timeout(TIMEOUT_MS);
    const res = await fetch(API_URL + path, { signal: signal ? AbortSignal.any([signal, timeout]) : timeout });
    return res.ok ? ((await res.json()) as T) : null;
  } catch {
    return null;
  }
}

// keepalive lets the request finish even if the reader leaves the page straight away.
// No body and no custom headers: the browser sends it without a CORS preflight.
export async function apiPost(path: string): Promise<boolean> {
  if (!API_URL) return false;
  try {
    const res = await fetch(API_URL + path, { method: "POST", keepalive: true, signal: AbortSignal.timeout(TIMEOUT_MS) });
    return res.ok;
  } catch {
    return false;
  }
}

// Counts one copy of a code block. The post is read from the address, because the code
// tabs are rendered from MDX and don't know which post they are in.
export function countCopy(lang: string) {
  const slug = /^\/posts\/([a-z0-9-]+)\/?$/.exec(window.location.pathname)?.[1];
  if (slug) void apiPost(`/api/v1/posts/${slug}/copies?lang=${encodeURIComponent(lang)}`);
}
