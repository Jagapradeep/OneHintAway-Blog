import type { Metadata } from "next";
import Link from "next/link";
import { INSTAGRAM_URL } from "@/lib/site";

export const metadata: Metadata = {
  title: "About | One Hint Away",
  description: "What One Hint Away is and how to use it.",
};

export default function AboutPage() {
  return (
    <article className="prose">
      <h1 className="chrome">About</h1>
      <p className="lead">
        One Hint Away teaches data structures and algorithms one pattern at a time, on Instagram at{" "}
        <a href={INSTAGRAM_URL} target="_blank" rel="noopener">
          @onehintaway
        </a>
        .
      </p>

      <h2>Two kinds of post</h2>
      <ul>
        <li>
          <strong>Pattern posts</strong> teach one idea: how to spot it in a problem, a dry run on a tiny input,
          the trap, and the code.
        </li>
        <li>
          <strong>Challenge posts</strong> take one hard problem and give hints one at a time, so you can stop as
          soon as you see the answer.
        </li>
      </ul>

      <h2>What this site adds</h2>
      <ul>
        <li>The slides, including the animated ones.</li>
        <li>Tested code in Java, Python, C++ and JavaScript, with a copy button. The site remembers your language.</li>
        <li>Practice problems you can click straight through to.</li>
      </ul>

      <p>
        New here? Read <Link href="/posts/start-here/">Start here</Link>, then follow the posts in order on the{" "}
        <Link href="/">home page</Link>, or jump to one in the <Link href="/patterns/">patterns index</Link>.
      </p>
    </article>
  );
}
