import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "One Hint Away",
  description: "DSA patterns, one hint at a time. Code in Java, Python, C++ and JavaScript.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
