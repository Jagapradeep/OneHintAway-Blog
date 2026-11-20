// Writes out/_headers after `next build`: the security headers Cloudflare sends with every
// page and file of the site (Workers static assets read this file; it is never served).
//
// The Content-Security-Policy is built from the same NEXT_PUBLIC_* settings the pages were
// built with, so it allows exactly the API, Umami and Turnstile this build talks to, and
// nothing else. Run by `npm run build` (postbuild); reads .env.local locally, like Next.
//
// What the policy does and doesn't do:
// - It limits where scripts may come from and where the page may send data (connect-src),
//   forbids plugins (object-src), <base> tricks, posting forms elsewhere, and being framed.
// - It allows inline scripts ('unsafe-inline'). A static export has no server to add a
//   per-request nonce, and Next.js writes page-specific inline scripts (the theme script and
//   its page data), so hashes would mean a different policy for every page. Injected inline
//   script is therefore not blocked; the site renders no user-written HTML, which is the
//   real defence against that.
//
// Report-only first: with ENFORCE_CSP false the browser blocks nothing for the policy; it only
// sends a report to the API (POST /api/v1/csp-report, counted in the csp_reports table) for
// everything the policy would have blocked. The other headers below are enforced either way.
// Once a week or two of reports shows nothing real, set ENFORCE_CSP to true; reports keep
// coming in after that, for anything a later change breaks.

import fs from "node:fs";
import path from "node:path";
import nextEnv from "@next/env";

const root = path.resolve(import.meta.dirname, "..");
nextEnv.loadEnvConfig(root, false);

function origin(value) {
  if (!value) return null;
  try {
    return new URL(value).origin;
  } catch {
    throw new Error(`write-headers: not a URL: ${value}`);
  }
}

// Report-only since 21 November 2026. Check the reports, then switch to true.
const ENFORCE_CSP = false;

const api = origin(process.env.NEXT_PUBLIC_API_URL);
const reportUrl = api ? `${api}/api/v1/csp-report` : null;
const umami = process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID ? origin(process.env.NEXT_PUBLIC_UMAMI_URL) : null;
const turnstile = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY ? "https://challenges.cloudflare.com" : null;

const list = (...items) => items.filter(Boolean).join(" ");
const csp = [
  "default-src 'self'",
  `script-src ${list("'self'", "'unsafe-inline'", umami, turnstile)}`,
  "style-src 'self' 'unsafe-inline'", // React style={} attributes and Turnstile's widget
  "img-src 'self' data:",
  "font-src 'self'",
  "media-src 'self'",
  `connect-src ${list("'self'", api, umami)}`,
  `frame-src ${turnstile ?? "'none'"}`,
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'",
  // Ask for https:// even where a page says http://, except when the API itself is plain
  // http (a local build against your laptop's API). Browsers ignore it in report-only mode.
  ENFORCE_CSP && !api?.startsWith("http:") ? "upgrade-insecure-requests" : null,
  // Where browsers send violation reports. Only report-uri: every current browser supports it,
  // and it was checked end to end (20 Nov). The newer report-to wins over it in Chrome when
  // both are present, and its delivery couldn't be confirmed, so it isn't added; the API
  // already accepts its format.
  reportUrl ? `report-uri ${reportUrl}` : null,
]
  .filter(Boolean)
  .join("; ");

const headers = {
  // Browsers use HTTPS only for a year, on onehintaway.com and every subdomain.
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  [ENFORCE_CSP ? "Content-Security-Policy" : "Content-Security-Policy-Report-Only"]: csp,
  // Files are what their Content-Type says; a browser must not guess "this text is a script".
  "X-Content-Type-Options": "nosniff",
  // No other site may show these pages in a frame (clickjacking). Old browsers read this one.
  "X-Frame-Options": "DENY",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  // Features the site never uses are switched off; fullscreen stays for the slide gallery.
  "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=(), fullscreen=(self)",
  // A page opened from here can't reach back into this tab, and the other way round.
  "Cross-Origin-Opener-Policy": "same-origin",
};

const out = path.join(root, "out");
if (!fs.existsSync(out)) throw new Error("write-headers: no out/ folder; run next build first");
const text = [
  "# Written by scripts/write-headers.mjs at build time. Do not edit: change the script.",
  "/*",
  ...Object.entries(headers).map(([name, value]) => `  ${name}: ${value}`),
  "",
].join("\n");
fs.writeFileSync(path.join(out, "_headers"), text);
console.log(
  `write-headers: out/_headers, CSP ${ENFORCE_CSP ? "enforced" : "report-only"} (connect-src: ${list("'self'", api, umami)}${turnstile ? "; Turnstile allowed" : ""})`,
);
