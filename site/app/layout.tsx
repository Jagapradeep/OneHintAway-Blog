import type { Metadata, Viewport } from "next";
import Link from "next/link";
import { Geist_Mono, Manrope, Sora } from "next/font/google";
import { BackButton } from "@/components/BackButton";
import { NavLinks } from "@/components/NavLinks";
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
  title: "One Hint Away · Learn DSA one pattern at a time",
  description:
    "A free, beginner-friendly way to learn data structures and algorithms: one pattern at a time, with slides, dry runs, tested code in Java, Python, C++ and JavaScript, and practice problems.",
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
    <html lang="en" className={`${sora.variable} ${manrope.variable} ${geistMono.variable}`} data-scroll-behavior="smooth" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>
        <a href="#main" className="skip-link">
          Skip to content
        </a>
        <div className="site-header-wrap">
          <header className="site-header">
            <Link href="/" className="brand" aria-label="One Hint Away, home">
              <span className="brand-mark" aria-hidden="true" />
              ONE HINT AWAY
            </Link>
            <NavLinks />
            <ThemeToggle />
          </header>
        </div>
        <main className="site-main" id="main" tabIndex={-1}>
          <BackButton />
          {children}
        </main>
        <div className="site-footer-wrap">
          <footer className="site-footer">
            <div className="footer-brand">
              <Link href="/" className="brand">
                <span className="brand-mark" aria-hidden="true" />
                ONE HINT AWAY
              </Link>
              <p>Learn data structures and algorithms one pattern at a time. Free, with code in four languages.</p>
            </div>
            <nav className="footer-links" aria-label="Footer">
              <p className="footer-heading">Learn</p>
              <Link href="/posts/start-here/">Start here</Link>
              <Link href="/patterns/">Patterns</Link>
              <Link href="/about/">About</Link>
            </nav>
            <div className="footer-links">
              <p className="footer-heading">Follow</p>
              <a href={INSTAGRAM_URL} target="_blank" rel="noopener">
                Instagram · @onehintaway
              </a>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
