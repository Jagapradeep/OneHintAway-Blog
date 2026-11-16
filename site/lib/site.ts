export const INSTAGRAM_URL = "https://www.instagram.com/onehintaway/";

// Umami analytics (self-hosted, no cookies). Both are public values set at build time;
// leave either one empty and no analytics script is added to the pages.
export const UMAMI_URL = (process.env.NEXT_PUBLIC_UMAMI_URL ?? "").replace(/\/+$/, "");
export const UMAMI_WEBSITE_ID = process.env.NEXT_PUBLIC_UMAMI_WEBSITE_ID ?? "";

// The live site's address, used for absolute URLs (sitemap, robots.txt). No trailing slash.
export const SITE_URL = "https://onehintaway.com";
