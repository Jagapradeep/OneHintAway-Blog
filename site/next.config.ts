import type { NextConfig } from "next";
import fs from "node:fs";
import path from "node:path";
import createMDX from "@next/mdx";

// Read as plain JSON so they can be passed to Shiki through Turbopack (options must be serialisable).
const readJson = (file: string) => JSON.parse(fs.readFileSync(path.join(process.cwd(), "lib", "shiki", file), "utf8"));
const intellijLight = readJson("intellij-light.json");
const pseudo = readJson("pseudo.tmLanguage.json");

const nextConfig: NextConfig = {
  // Build to plain HTML/CSS/JS in out/, so Cloudflare Pages can serve it with no server.
  output: "export",
  // /posts/x/ becomes posts/x/index.html, which every static host serves correctly.
  trailingSlash: true,
  // The default image optimizer needs a server; static export can't use it.
  images: { unoptimized: true },
  pageExtensions: ["ts", "tsx", "md", "mdx"],
};

const withMDX = createMDX({
  options: {
    // Plugin names as strings so they work with Turbopack.
    // remark-frontmatter strips the YAML header so it isn't rendered as text.
    // Our own plugin is passed as an absolute path: @next/mdx resolves names
    // relative to each .mdx file, so a "./lib/..." path would break.
    remarkPlugins: [
      "remark-frontmatter",
      "remark-gfm",
      path.join(process.cwd(), "lib", "remark-code-tabs.mjs"),
    ],
    // Syntax colours added at build time (no JavaScript sent to readers), using VS Code's
    // own grammars. Dark theme: VS Code "Dark+". Light theme: IntelliJ Light colours
    // (lib/shiki/intellij-light.json), stored in --shiki-light (see globals.css).
    // Fences without a language are the pseudocode: lib/shiki/pseudo.tmLanguage.json.
    rehypePlugins: [
      [
        "@shikijs/rehype",
        {
          themes: { dark: "dark-plus", light: intellijLight },
          defaultColor: "dark",
          langs: ["java", "python", "cpp", "javascript", pseudo],
          defaultLanguage: "pseudo",
          addLanguageClass: true,
        },
      ],
    ],
  },
});

export default withMDX(nextConfig);
