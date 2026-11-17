"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";

// Next.js only scrolls to the top after a link when the new page's top is off screen. While the
// page swaps, the document can be short for a moment, so the browser pulls the old scroll position
// down to a few dozen pixels; Next.js then sees the new content's top on screen and leaves the page
// slightly scrolled. This puts every new page at the top. Back and forward keep the browser's own
// position, and links to a #section are left to the browser.
export function ScrollReset() {
  const pathname = usePathname();
  const first = useRef(true);
  const traversing = useRef(false);

  useEffect(() => {
    const onPop = () => {
      traversing.current = true;
    };
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  useEffect(() => {
    if (first.current) {
      first.current = false;
      return;
    }
    if (traversing.current) {
      traversing.current = false;
      return;
    }
    if (window.location.hash) return;
    window.scrollTo({ top: 0, left: 0, behavior: "instant" });
  }, [pathname]);

  return null;
}
