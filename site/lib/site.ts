export const INSTAGRAM_URL = "https://www.instagram.com/onehintaway/";

// The newsletter sign-up form shows only when this is "on" (and the API address is set).
// Keep it off until the API can really send the confirmation email (RESEND_API_KEY).
export const SIGNUP_ON = process.env.NEXT_PUBLIC_SIGNUP === "on";

// Reader accounts (sign in by emailed link, progress ticks). Everything about them shows
// only when this is "on" and the API address is set; otherwise the site is built without them.
export const ACCOUNTS_ON = process.env.NEXT_PUBLIC_ACCOUNTS === "on" && !!process.env.NEXT_PUBLIC_API_URL;

// Umami analytics (self-hosted, no cookies). Both are public values set at build time;
// leave either one empty and no analytics script is added to the pages.
export const UMAMI_URL = (process.env.NEXT_PUBLIC_UMAMI_URL ?? "").replace(/\/+$/, "");
export const UMAMI_WEBSITE_ID = process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID ?? "";

// The live site's address, used for absolute URLs (sitemap, robots.txt). No trailing slash.
export const SITE_URL = "https://onehintaway.com";
