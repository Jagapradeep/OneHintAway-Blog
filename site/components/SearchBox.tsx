"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { apiGet } from "@/lib/api";

type Hit = { slug: string; number: number; title: string; pattern: string; section: string };
type Result = { q: string; hits: Hit[] | null };

// Header search: a round button that opens a small panel with a box and live results.
// It is a button, not an always-open box, so the header keeps its height and fits a phone.
// Only rendered when the site was built with an API address (see lib/api.ts).
export function SearchBox() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  // The answer to one query; hits is null when the API could not be reached.
  const [result, setResult] = useState<Result | null>(null);
  const rootRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const term = q.trim();

  // Ask a moment after the reader stops typing; drop the answer to anything older.
  useEffect(() => {
    if (!term) return;
    const abort = new AbortController();
    const timer = setTimeout(async () => {
      const hits = await apiGet<Hit[]>(`/api/v1/search?q=${encodeURIComponent(term)}`, abort.signal);
      if (!abort.signal.aborted) setResult({ q: term, hits });
    }, 250);
    return () => {
      clearTimeout(timer);
      abort.abort();
    };
  }, [term]);

  // Close on Escape or a click outside.
  useEffect(() => {
    if (!open) return;
    inputRef.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    const onDown = (e: PointerEvent) => !rootRef.current?.contains(e.target as Node) && setOpen(false);
    document.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onDown);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("pointerdown", onDown);
    };
  }, [open]);

  const current = result && result.q === term ? result : null;

  return (
    <div className="search" ref={rootRef}>
      <button
        type="button"
        className="search-toggle"
        aria-label="Search posts"
        aria-expanded={open}
        aria-controls="search-panel"
        onClick={() => setOpen((o) => !o)}
      >
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <circle cx="11" cy="11" r="6.5" />
          <path d="m16 16 4.5 4.5" />
        </svg>
      </button>
      {open && (
        <div className="search-panel" id="search-panel">
          <input
            ref={inputRef}
            type="search"
            className="search-input"
            placeholder="Search posts"
            aria-label="Search posts"
            maxLength={100}
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <div aria-live="polite">
            {term && current && current.hits === null && <p className="search-note">Search is not available right now.</p>}
            {term && current && current.hits?.length === 0 && <p className="search-note">No posts match.</p>}
            {term && current && current.hits && current.hits.length > 0 && (
              <ul className="search-results">
                {current.hits.map((h) => (
                  <li key={h.slug}>
                    <Link href={`/posts/${h.slug}/`} onClick={() => setOpen(false)}>
                      <span className="search-num">{String(h.number).padStart(2, "0")}</span>
                      <span className="search-title">{h.title}</span>
                      <span className="search-pattern">{h.pattern}</span>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
