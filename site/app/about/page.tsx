import type { Metadata } from "next";
import Link from "next/link";
import { API_URL } from "@/lib/api";
import { ACCOUNTS_ON, INSTAGRAM_URL, SIGNUP_ON } from "@/lib/site";

export const metadata: Metadata = {
  title: "About | One Hint Away",
  description:
    "One Hint Away teaches data structures and algorithms one pattern at a time: slides, tested code in four languages, and hard problems one hint at a time.",
};

export default function AboutPage() {
  return (
    <article className="prose">
      <h1 className="chrome">About</h1>
      <p className="lead">
        You understand the tutorial, then open a problem on your own and your mind goes blank. One Hint Away is for
        that moment. It teaches data structures and algorithms one pattern at a time, and gives hard problems one hint
        at a time, so you do the solving.
      </p>
      <p>
        It started on Instagram at{" "}
        <a href={INSTAGRAM_URL} target="_blank" rel="noopener">
          @onehintaway
        </a>
        . This site is its home: every post, with everything that doesn&apos;t fit in a carousel.
      </p>

      <h2>Who it&apos;s for</h2>
      <ul>
        <li>You are starting DSA and want one clear order to learn it in.</li>
        <li>You are preparing for coding interviews and want to recognise patterns, not memorise answers.</li>
        <li>You know a pattern in theory but freeze when a problem doesn&apos;t name it.</li>
      </ul>

      <h2>Two kinds of post</h2>
      <ul>
        <li>
          <strong>Pattern posts</strong> teach one idea: the clue in a problem that gives it away, an everyday
          example, a dry run on a tiny input, a pseudocode template you can reuse, and two problems to practise.
        </li>
        <li>
          <strong>Hint ladders</strong> take one hard problem. You try it first; each step gives one more hint, and
          you stop as soon as you see the answer. The full solution comes last.
        </li>
      </ul>

      <h2>What you get here</h2>
      <ul>
        <li>The full slides, including the animated ones, with a full-screen view.</li>
        <li>
          Code in Java, Python, C++ and JavaScript, checked against a brute-force answer before it is published. Copy
          it in one click; the site remembers your language.
        </li>
        <li>Practice problems you can click straight through to.</li>
        <li>
          The <Link href="/visualize/">visualizer</Link>: watch a pattern run step by step, on your own input.
        </li>
        {ACCOUNTS_ON && <li>A free account that ticks off the lessons you have finished, so you can see where you stopped.</li>}
        {API_URL && SIGNUP_ON && <li>New patterns by email, with the form at the bottom of every page. Nothing else.</li>}
      </ul>

      <h2>How to use it</h2>
      <ol>
        <li>
          Read <Link href="/posts/start-here/">Start here</Link> for the map: about 90 posts in stages, each building
          on the last.
        </li>
        <li>
          Follow the posts in order from the <Link href="/">home page</Link>, or jump to one pattern in the{" "}
          <Link href="/patterns/">patterns index</Link>.
        </li>
        <li>Try each practice problem before you look at the code. The struggle is where the pattern sticks.</li>
      </ol>

      <h2>Get in touch</h2>
      <p>
        Found a mistake, or want a pattern covered? Send a message on{" "}
        <a href={INSTAGRAM_URL} target="_blank" rel="noopener">
          Instagram
        </a>{" "}
        or email <a href="mailto:hello@onehintaway.com">hello@onehintaway.com</a>.
      </p>
    </article>
  );
}
