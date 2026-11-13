"use client";

import { useEffect, useRef, useState } from "react";

type Item = { id: string; name: string; count: number };

// Pattern list for the patterns page. Wide screens: a sticky sidebar on the left.
// Narrow screens: a sticky row of chips under the header. Either way it never scrolls away.
// Clicking a pattern scrolls the content to it and keeps that pattern highlighted;
// scrolling by hand moves the highlight to whichever pattern is at the top (scroll-spy).
export function PatternNav({ items, total }: { items: Item[]; total: number }) {
  const [active, setActive] = useState(items[0]?.id ?? "");
  // After a click the spy waits until the reader scrolls by hand. So the highlight doesn't
  // flicker through every pattern on the way, and a pattern near the page end, which can't
  // reach the top of the window, stays highlighted once the scroll stops.
  const lockRef = useRef(false);
  const listRef = useRef<HTMLUListElement>(null);

  useEffect(() => {
    const ids = items.map((i) => i.id);
    let raf = 0;

    const spy = () => {
      raf = 0;
      if (lockRef.current) return;
      const first = document.getElementById(ids[0]);
      if (!first) return;
      const offset = parseFloat(getComputedStyle(first).scrollMarginTop) || 0;
      // The pattern being read is the last one whose heading has passed a reading line.
      // That line sits under the header for most of the page. The last few patterns can't
      // scroll up that far, so over the final stretch of scrolling the line slides down to
      // the bottom of the window: each of them gets its turn, in order, and none is skipped.
      const vh = window.innerHeight;
      const max = document.documentElement.scrollHeight - vh;
      const range = Math.min(max, vh - offset);
      const t = range > 0 ? Math.min(1, Math.max(0, (window.scrollY - (max - range)) / range)) : 1;
      const line = offset + (vh - offset) * t;
      let current = ids[0];
      for (const id of ids) {
        const el = document.getElementById(id);
        if (el && el.getBoundingClientRect().top - line <= 4) current = id;
      }
      setActive(current);
    };
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(spy);
    };
    // Only the reader's own scrolling releases the spy. Releasing it when the click's scroll
    // ended let one last queued scroll update run and move the highlight off the clicked pattern.
    const unlock = () => {
      lockRef.current = false;
    };

    // Arrived with #pattern in the address: highlight it.
    const fromHash = decodeURIComponent(location.hash.slice(1));
    if (ids.includes(fromHash)) setActive(fromHash);
    else spy();

    window.addEventListener("scroll", onScroll, { passive: true });
    // Any hand scrolling takes over from a click straight away (pointerdown covers the scrollbar;
    // on a link it comes before the click, which locks again).
    window.addEventListener("pointerdown", unlock, { passive: true });
    window.addEventListener("wheel", unlock, { passive: true });
    window.addEventListener("touchstart", unlock, { passive: true });
    window.addEventListener("keydown", unlock);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("pointerdown", unlock);
      window.removeEventListener("wheel", unlock);
      window.removeEventListener("touchstart", unlock);
      window.removeEventListener("keydown", unlock);
    };
  }, [items]);

  // Keep the highlighted pattern visible inside the list (it scrolls on its own when long),
  // without moving the page.
  useEffect(() => {
    const list = listRef.current;
    const link = list?.querySelector<HTMLElement>(`[data-id="${active}"]`);
    if (!list || !link) return;
    const horizontal = list.scrollWidth > list.clientWidth + 1;
    if (horizontal) {
      const left = link.offsetLeft - list.clientWidth / 2 + link.offsetWidth / 2;
      list.scrollTo({ left, behavior: "smooth" });
    } else if (list.scrollHeight > list.clientHeight + 1) {
      const { offsetTop: top, offsetHeight: h } = link;
      if (top < list.scrollTop || top + h > list.scrollTop + list.clientHeight) {
        list.scrollTo({ top: top - list.clientHeight / 2 + h / 2, behavior: "smooth" });
      }
    }
  }, [active]);

  function go(e: React.MouseEvent<HTMLAnchorElement>, id: string) {
    const target = document.getElementById(id);
    if (!target) return;
    e.preventDefault();
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    lockRef.current = true;
    setActive(id);
    target.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    // Keyboard and screen-reader users land on the pattern they picked.
    target.focus({ preventScroll: true });
    history.replaceState(null, "", `#${id}`);
  }

  return (
    <nav className="pattern-nav" aria-label="Patterns">
      <p className="pattern-nav-title">
        {items.length} patterns <span>· {total} lessons</span>
      </p>
      <ul ref={listRef}>
        {items.map((it) => (
          <li key={it.id}>
            <a
              href={`#${it.id}`}
              data-id={it.id}
              className={it.id === active ? "is-active" : undefined}
              aria-current={it.id === active ? "location" : undefined}
              onClick={(e) => go(e, it.id)}
            >
              <span className="pattern-nav-name">{it.name}</span>
              <span className="pattern-nav-count" aria-label={`${it.count} lesson${it.count > 1 ? "s" : ""}`}>
                {it.count}
              </span>
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
