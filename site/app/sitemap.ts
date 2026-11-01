import type { MetadataRoute } from "next";
import { getAllPosts } from "@/lib/posts";
import { SITE_URL } from "@/lib/site";

// Written to out/sitemap.xml at build time (static export).
export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  const built = new Date();
  // Top-level pages. "Start here" is a post, so it comes in with the posts below.
  const pages = ["/", "/patterns/", "/about/"].map((path) => ({
    url: `${SITE_URL}${path}`,
    lastModified: built,
  }));
  const posts = getAllPosts().map((p) => ({
    url: `${SITE_URL}/posts/${p.slug}/`,
    lastModified: p.published,
  }));
  return [...pages, ...posts];
}
