import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { UnsubscribeLink } from "@/components/UnsubscribeLink";
import { API_URL } from "@/lib/api";

// The page the "Unsubscribe" button in an email opens: /unsubscribe/#token=...
// The token stays after "#", so it never reaches a server or the analytics script.
// The page itself posts it to the API as soon as it loads (see UnsubscribeLink).
export const metadata: Metadata = {
  title: "Unsubscribe | One Hint Away",
  description: "Stop getting new patterns by email.",
  robots: { index: false, follow: false },
  referrer: "no-referrer",
};

// Runs while the page loads, before the analytics script: keeps the token in memory and
// takes it out of the address bar.
const stashToken = `(function(){var h=location.hash;if(h.indexOf("token=")>-1){window.__ohwUnsub=h;history.replaceState(null,"",location.pathname)}})()`;

export default function UnsubscribePage() {
  if (!API_URL) notFound();
  return (
    <article className="prose subscribed">
      <script dangerouslySetInnerHTML={{ __html: stashToken }} />
      <UnsubscribeLink />
    </article>
  );
}
