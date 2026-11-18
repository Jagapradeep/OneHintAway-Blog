import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { SignInPage } from "@/components/SignInPage";
import { ACCOUNTS_ON } from "@/lib/site";

export const metadata: Metadata = {
  title: "Sign in | One Hint Away",
  description: "Sign in to One Hint Away.",
  robots: { index: false, follow: false },
};

export default function SignIn() {
  if (!ACCOUNTS_ON) notFound();
  return (
    <article className="prose acct-page">
      <SignInPage />
    </article>
  );
}
