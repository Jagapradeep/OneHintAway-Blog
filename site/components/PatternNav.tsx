"use client";

import { useEffect, useRef, useState } from "react";

type Item = { id: string; name: string; count: number };

// Pattern list for the patterns page. Wide screens: a sticky sidebar on the left.
// Narrow screens: a sticky row of chips under the header. Either way it never scrolls away.
// Clicking a pattern scrolls the content to it and keeps that pattern highlighted;
// scrolling by hand moves the highlight to whichever pattern is at the top (scroll-spy).
export function PatternNav({ items, total }: { items: Item[]; total: number }) {
  const [active, setActive] = useState(items[0]?.id ?? "");
  // While a click's smooth scroll runs, the spy waits, so the highlight doesn't flicker
  // through every pattern on the way.
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
      let current = ids[0];
      for (const id of ids) {
        const el = document.getElementById(id);
        if (el && el.getBoundingClientRect().top - offset <= 4) current = id;
      }
      // On phones the last few patterns can't scroll up to the top, so at the very bottom
      // of the page the last pattern is the one being read.
      const atBottom = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2;
      if (atBottom) current = ids[ids.length - 1];
      setActive(current);
    };
    const onScroll = () => {
      if (!raf) raf = requestAnimationFrame(spy);
    };
    // Release the spy without re-checking: the clicked pattern stays highlighted even if it
    // couldn't reach the top (near the page end). The next real scroll updates it.
    const unlock = () => {
      lockRef.current = false;
    };

    // Arrived with #pattern in the address: highlight it.
    const fromHash = decodeURIComponent(location.hash.slice(1));
    if (ids.includes(fromHash)) setActive(fromHash);
    else spy();

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("scrollend", unlock);
    // Any hand scrolling takes over from a click straight away.
    window.addEventListener("wheel", unlock, { passive: true });
    window.addEventListener("touchstart", unlock, { passive: true });
    window.addEventListener("keydown", unlock);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("scrollend", unlock);
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
    // Browsers without the scrollend event: release the spy after the scroll has had time.
    if (!("onscrollend" in window)) setTimeout(() => (lockRef.current = false), reduce ? 50 : 900);
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
              <span className="pattern-nav-count">{it.count}</span>
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
