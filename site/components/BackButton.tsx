"use client";

import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";

// "Back" at the top of every page except home. It lives in the root layout, which stays
// mounted across page changes, so it can remember the pages visited inside the site.
// Came from another page here: go back to it. Landed here directly (from Instagram,
// Google, a shared link): go to the home page instead of leaving the site.
export function BackButton() {
  const pathname = usePathname();
  const router = useRouter();
  // Pages visited in this tab, oldest first. Arriving at the page just before the
  // current one counts as going back (browser back button or this button).
  const [trail, setTrail] = useState<string[]>([pathname]);

  // Update the trail when the page changes (React's "adjust state during render" pattern).
  if (trail[trail.length - 1] !== pathname) {
    const t = trail;
    setTrail(t.length > 1 && t[t.length - 2] === pathname ? t.slice(0, -1) : [...t, pathname]);
  }

  if (pathname === "/") return null;
  const canGoBack = trail.length > 1;

  return (
    <button
      type="button"
      className="back-button"
      onClick={() => (canGoBack ? router.back() : router.push("/"))}
    >
      <span aria-hidden="true">←</span> {canGoBack ? "Back" : "All posts"}
    </button>
  );
}
