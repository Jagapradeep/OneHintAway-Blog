// Free and paid patterns. Every pattern has a tier in its own file.
//
// PAYWALL_ON is off until there is a login, a payment and a server check.
// While it is off, every pattern is fully open. Turning it on makes a paid
// pattern a preview: it plays the post's example, without the reader's own
// input. That alone is a courtesy lock, not protection: the code still reaches
// every browser. Real protection means serving paid chunks (loaders.ts) only
// after a server has checked the reader's access.
import type { Pattern } from "./schema.ts";

export const PAYWALL_ON = false;

export function isLocked(p: Pick<Pattern, "tier">): boolean {
  return PAYWALL_ON && p.tier === "paid";
}
