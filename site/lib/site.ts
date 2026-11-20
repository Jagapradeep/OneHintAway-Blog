export const INSTAGRAM_URL = "https://www.instagram.com/onehintaway/";

// The footer's "new patterns by email" form: shown whenever the API address is set.
// NEXT_PUBLIC_SIGNUP=off hides it (for example while email sending is broken).
export const SIGNUP_ON = process.env.NEXT_PUBLIC_SIGNUP !== "off";

// Reader accounts (sign in by emailed link, progress ticks). Everything about them shows
// only when this is "on" and the API address is set; otherwise the site is built without them.
export const ACCOUNTS_ON = process.env.NEXT_PUBLIC_ACCOUNTS === "on" && !!process.env.NEXT_PUBLIC_API_URL;

// Cloudflare Turnstile site key (public). When set, the sign-in form runs Turnstile and sends
// its token with the code request; the API checks it with the secret key before emailing a code.
// Leave it out locally: the API on your laptop has no secret and doesn't ask for a token.
export const TURNSTILE_SITE_KEY = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY ?? "";

// Umami analytics (self-hosted, no cookies). Both are public values set at build time;
// leave either one empty and no analytics script is added to the pages.
export const UMAMI_URL = (process.env.NEXT_PUBLIC_UMAMI_URL ?? "").replace(/\/+$/, "");
export const UMAMI_WEBSITE_ID = process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID ?? "";

// The live site's address, used for absolute URLs (sitemap, robots.txt). No trailing slash.
export const SITE_URL = "https://onehintaway.com";

// localStorage key meaning "this browser has signed in before" (see lib/account.ts).
export const ACCOUNT_FLAG = "ohw.account";

// Runs in <head> before the page paints, so a reader who has signed in before never sees
// "Sign in" flash in the header while the API is asked who they are.
export const ACCOUNT_SCRIPT = `try{if(localStorage.getItem("${ACCOUNT_FLAG}")!==null)document.documentElement.dataset.acct="1"}catch(e){}`;
