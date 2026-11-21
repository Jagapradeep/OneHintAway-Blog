"use client";

import { type RefObject, useEffect } from "react";

// While a header panel (search, account) is open, the page behind it must not scroll: a
// swipe or wheel inside the panel used to move the page, and on phones (where the header
// scrolls away) it carried the panel off the screen with it. The page is locked; the panel
// scrolls on its own if it is taller than what's visible (a small phone, or a phone with
// the keyboard open), so its last button is always reachable.

let locks = 0;
let saved = { overflow: "", gutter: "" };

function lock() {
  const root = document.documentElement;
  if (locks++ > 0) return;
  saved = { overflow: root.style.overflow, gutter: root.style.scrollbarGutter };
  // Keep the scrollbar's space on desktop, so the page doesn't jump sideways.
  if (window.innerWidth > root.clientWidth) root.style.scrollbarGutter = "stable";
  root.style.overflow = "hidden";
}

function unlock() {
  if (--locks > 0) return;
  const root = document.documentElement;
  root.style.overflow = saved.overflow;
  root.style.scrollbarGutter = saved.gutter;
}

export function usePanelLock(open: boolean, panel: RefObject<HTMLElement | null>) {
  useEffect(() => {
    if (!open) return;
    lock();
    const vv = window.visualViewport;
    // As tall as the space below the panel's top that's visible now (keyboard included).
    // Set as --panel-room on the page root; the panels' CSS reads it.
    const fit = () => {
      const top = panel.current?.getBoundingClientRect().top;
      if (top === undefined) return;
      const bottom = vv ? vv.offsetTop + vv.height : window.innerHeight;
      document.documentElement.style.setProperty("--panel-room", `${Math.max(160, Math.floor(bottom - top - 12))}px`);
    };
    fit();
    vv?.addEventListener("resize", fit);
    vv?.addEventListener("scroll", fit);
    window.addEventListener("resize", fit);
    return () => {
      vv?.removeEventListener("resize", fit);
      vv?.removeEventListener("scroll", fit);
      window.removeEventListener("resize", fit);
      document.documentElement.style.removeProperty("--panel-room");
      unlock();
    };
  }, [open, panel]);
}
