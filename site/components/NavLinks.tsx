"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "/posts/start-here/", label: "Start here" },
  { href: "/patterns/", label: "Patterns" },
  { href: "/about/", label: "About" },
];

// Main navigation, with the current page marked.
export function NavLinks() {
  const pathname = usePathname();
  const here = (href: string) => pathname === href || pathname === href.replace(/\/$/, "");
  return (
    <nav className="site-nav" aria-label="Main">
      {LINKS.map((l) => (
        <Link key={l.href} href={l.href} aria-current={here(l.href) ? "page" : undefined}>
          {l.label}
        </Link>
      ))}
    </nav>
  );
}
