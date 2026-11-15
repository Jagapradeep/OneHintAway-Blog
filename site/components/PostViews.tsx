"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";

// Counts this visit, then shows the post's view count as one more pill in the meta row.
// Renders nothing until a count arrives, and nothing at all if the API is unreachable.
export function PostViews({ slug }: { slug: string }) {
  const [views, setViews] = useState<number | null>(null);

  useEffect(() => {
    let gone = false;
    (async () => {
      await apiPost(`/api/v1/posts/${slug}/views`);
      const stats = await apiGet<{ views: number }>(`/api/v1/posts/${slug}/stats`);
      if (!gone && stats && stats.views > 0) setViews(stats.views);
    })();
    return () => {
      gone = true;
    };
  }, [slug]);

  if (views === null) return null;
  return (
    <li>
      <svg className="post-meta-icon" viewBox="0 0 20 20" aria-hidden="true" focusable="false">
        <path d="M2 10s3-5.5 8-5.5S18 10 18 10s-3 5.5-8 5.5S2 10 2 10Z" />
        <circle cx="10" cy="10" r="2.3" />
      </svg>
      {views.toLocaleString("en")} {views === 1 ? "view" : "views"}
    </li>
  );
}
