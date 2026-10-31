import type { Metadata, Viewport } from "next";
import Link from "next/link";
import { Geist_Mono, Manrope, Sora } from "next/font/google";
import { BackButton } from "@/components/BackButton";
import { ThemeToggle } from "@/components/ThemeToggle";
import { INSTAGRAM_URL } from "@/lib/site";
import { themeScript } from "@/lib/theme";
import "./globals.css";

// Same fonts as the Instagram slides (Graphite & Chrome v3.1).
// next/font downloads them at build time and serves them from this site,
// so readers' browsers never call Google.
const sora = Sora({ subsets: ["latin"], weight: ["600", "700", "800"], variable: "--font-title" });
const manrope = Manrope({ subsets: ["latin"], weight: ["500", "600", "700"], variable: "--font-body" });
const geistMono = Geist_Mono({ subsets: ["latin"], weight: ["500", "600"], variable: "--font-mono" });

export const metadata: Metadata = {
  title: "One Hint Away",
  description: "DSA patterns, one hint at a time. Code in Java, Python, C++ and JavaScript.",
};

// Phone browser bar colour follows the device theme.
export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: dark)", color: "#08090b" },
    { media: "(prefers-color-scheme: light)", color: "#f5f6f8" },
  ],
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    // suppressHydrationWarning: the theme script and browser extensions (e.g. QuillBot's
    // data-qb-installed) add attributes to <html> before React loads. This only ignores
    // attribute differences on <html> itself, not anywhere inside the page.
    <html lang="en" className={`${sora.variable} ${manrope.variable} ${geistMono.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>
        <header className="site-header">
          <Link href="/" className="brand" aria-label="One Hint Away, home">
            <span className="brand-mark" aria-hidden="true" />
            ONE HINT AWAY
          </Link>
          <nav className="site-nav" aria-label="Main">
            <Link href="/posts/start-here/">Start here</Link>
            <Link href="/patterns/">Patterns</Link>
            <Link href="/about/">About</Link>
          </nav>
          <ThemeToggle />
        </header>
        <main className="site-main">
          <BackButton />
          {children}
        </main>
        <footer className="site-footer">
          <a href={INSTAGRAM_URL} target="_blank" rel="noopener">
            @onehintaway
          </a>
          <span>DSA patterns, one hint at a time.</span>
        </footer>
      </body>
    </html>
  );
}
