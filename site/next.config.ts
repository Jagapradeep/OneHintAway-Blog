import type { NextConfig } from "next";
import path from "node:path";
import createMDX from "@next/mdx";

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
  },
});

export default withMDX(nextConfig);
