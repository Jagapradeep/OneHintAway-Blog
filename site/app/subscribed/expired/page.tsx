import type { Metadata } from "next";
import Link from "next/link";
import { ConfirmSteps } from "@/components/ConfirmSteps";

// Where the API sends a reader whose confirmation link it did not recognise.
export const metadata: Metadata = {
  title: "That link didn't work | One Hint Away",
  description: "The confirmation link was not recognised.",
  robots: { index: false, follow: false },
};

export default function ExpiredPage() {
  return (
    <article className="prose subscribed">
      <h1 className="chrome">That link didn&apos;t work.</h1>
      <p className="lead">Your email is not confirmed yet.</p>

      <ConfirmSteps at={1} />

      <p>
        The link was incomplete or is not one we sent. This usually happens when a mail app cuts a long link in two.
      </p>
      <ul>
        <li>Open the email again and use the button, or copy the whole link into your browser.</li>
        <li>Or sign up once more from the foot of any page, and a fresh link is sent.</li>
      </ul>
      <p className="subscribed-actions">
        <Link href="/" className="button">
          Back to the site
        </Link>
      </p>
    </article>
  );
}
