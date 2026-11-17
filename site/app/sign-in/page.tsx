import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SignInLink } from "@/components/SignInLink";
import { ACCOUNTS_ON } from "@/lib/site";

// The page an emailed sign-in link opens: /sign-in/#token=...
// It is a static page, so opening the link (as mail scanners do) changes nothing. The
// reader presses "Sign in" here, and only that sends the token to the API.
export const metadata: Metadata = {
  title: "Sign in | One Hint Away",
  description: "Sign in to One Hint Away.",
  robots: { index: false, follow: false },
  referrer: "no-referrer",
};

// Runs while the page is still loading, before the analytics script: it takes the token
// out of the address bar, so it is never recorded anywhere, and keeps it in memory for
// the button (lib/account.ts picks it up).
const stashToken = `(function(){var h=location.hash;if(h.indexOf("token=")>-1){window.__ohwLink=h;history.replaceState(null,"",location.pathname)}})()`;

export default function SignInPage() {
  if (!ACCOUNTS_ON) notFound();
  return (
    <article className="prose acct-page">
      <script dangerouslySetInnerHTML={{ __html: stashToken }} />
      <SignInLink />
    </article>
  );
}
