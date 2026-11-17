import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ACCOUNTS_ON } from "@/lib/site";

export const metadata: Metadata = {
  title: "Privacy | One Hint Away",
  description: "What One Hint Away stores about you, why, and how to delete it all.",
  alternates: { canonical: "/privacy/" },
};

export default function PrivacyPage() {
  if (!ACCOUNTS_ON) notFound();
  return (
    <article className="prose acct-page">
      <h1 className="chrome">Privacy</h1>
      <p className="lead">What this site stores about you, why, and how to delete it all. In plain words.</p>

      <h2>Reading needs no account</h2>
      <p>
        Every lesson is free to read without signing in. An account only adds one thing: it remembers which lessons
        you have finished.
      </p>

      <h2>What is stored when you sign in</h2>
      <ul>
        <li>
          <strong>Your email address.</strong> It is how you sign in: we email you a link, and there is no password.
        </li>
        <li>
          <strong>The lessons you marked as done</strong>, and when you marked each one.
        </li>
        <li>
          <strong>One record for each device you are signed in on.</strong> It holds a scrambled copy (a hash) of a
          random code, and the times it was created and last used. Your browser keeps the code itself in one cookie.
          The stored copy can&apos;t be turned back into the code.
        </li>
        <li>
          <strong>Sign-in links, for a short time.</strong> Each link is kept as a scrambled copy next to your email
          address. A link stops working after 15 minutes or after one use, and old ones are removed.
        </li>
      </ul>
      <p>Nothing else: no name, no password, and no list of the pages you read.</p>

      <h2>Why</h2>
      <p>
        The email address is needed to send the sign-in link and to know it is you next time. The finished lessons
        are what you asked the site to remember. The device record is what keeps you signed in for 30 days after
        your last visit. Your address is not sold or shared, and signing in does not put you on any mailing list.
      </p>

      <h2>The cookie</h2>
      <p>
        Signing in sets one cookie. It only keeps you signed in. Page scripts can&apos;t read it, and it is sent
        only to this site&apos;s own server. There are no advertising or tracking cookies. Your browser also remembers
        your light or dark theme, your last code language, and the fact that you have signed in before.
      </p>

      <h2>The newsletter is separate</h2>
      <p>
        You get new patterns by email only if you ask for them (the box in the sign-in panel, or the form at the
        bottom of the page) and then confirm through the email we send. Deleting your account does not change the
        newsletter. To stop it, write to <a href="mailto:hello@onehintaway.com">hello@onehintaway.com</a>.
      </p>

      <h2>Visits and counts</h2>
      <p>
        The site counts page views without cookies and without storing your internet address. The count you see on a
        lesson uses a scrambled value that changes every day, so visits can&apos;t be tied to you or linked across
        days.
      </p>

      <h2>Who else handles it</h2>
      <p>
        Emails are sent through Resend, so your address passes through their service. The database runs on a server
        rented from DigitalOcean, and the pages are served by Cloudflare.
      </p>

      <h2>How to delete it all</h2>
      <ol>
        <li>Sign in, open the account button at the top right, and choose Delete account.</li>
        <li>We email you a fresh link, to make sure it is you. Open it and confirm.</li>
      </ol>
      <p>
        That removes your email address, every device record and your finished lessons straight away. Nightly backups
        hold a copy for up to 14 days and are then deleted. If you can&apos;t sign in, write to{" "}
        <a href="mailto:hello@onehintaway.com">hello@onehintaway.com</a> from the address in question and we will
        delete it for you.
      </p>
    </article>
  );
}
