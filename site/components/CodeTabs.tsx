"use client";

import { createContext, useContext, useRef, useState, useSyncExternalStore, type ReactNode } from "react";

export const LANG_LABELS: Record<string, string> = {
  java: "Java",
  python: "Python",
  cpp: "C++",
  javascript: "JavaScript",
};
// Shorter tab names for phones, so the tabs and the Copy button fit on one row.
const SHORT_LABELS: Record<string, string> = { javascript: "JS" };
const ORDER = ["java", "python", "cpp", "javascript"];
const STORAGE_KEY = "ohw.lang";
const CHANGE_EVENT = "ohw-lang-change";

// The reader's last-picked language, shared by every tab group on the page and
// remembered across visits. localStorage can throw (private mode), so it is guarded.
function readLang(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}
function writeLang(lang: string) {
  try {
    localStorage.setItem(STORAGE_KEY, lang);
  } catch {
    /* ignore */
  }
  window.dispatchEvent(new Event(CHANGE_EVENT));
}
function subscribe(onChange: () => void) {
  window.addEventListener(CHANGE_EVENT, onChange);
  window.addEventListener("storage", onChange);
  return () => {
    window.removeEventListener(CHANGE_EVENT, onChange);
    window.removeEventListener("storage", onChange);
  };
}

const ActiveLang = createContext<string>("java");

export function CodeTabs({ children, langs }: { children: ReactNode; langs?: string }) {
  // Build-time HTML has no localStorage, so the server snapshot is null (shows the first tab).
  const saved = useSyncExternalStore(subscribe, readLang, () => null);
  const available = langs ? langs.split(",") : ORDER;
  const active = saved && available.includes(saved) ? saved : available[0];
  const boxRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = useState(false);

  async function copy() {
    const code = boxRef.current?.querySelector(`[data-lang="${active}"] pre`)?.textContent ?? "";
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard blocked: do nothing */
    }
  }

  return (
    <div className="code-tabs" ref={boxRef}>
      {/* Tabs and Copy share one row. The tabs scroll sideways if they ever run out of room,
          and on phones Copy shrinks to an icon, so it never wraps onto a line of its own. */}
      <div className="code-tabs-bar">
        <div className="code-tabs-list" role="tablist">
          {available.map((l) => (
            <button
              key={l}
              role="tab"
              aria-selected={l === active}
              className={l === active ? "active" : undefined}
              onClick={() => writeLang(l)}
              aria-label={SHORT_LABELS[l] ? LANG_LABELS[l] : undefined}
            >
              {SHORT_LABELS[l] ? (
                <>
                  <span className="tab-full">{LANG_LABELS[l]}</span>
                  <span className="tab-short">{SHORT_LABELS[l]}</span>
                </>
              ) : (
                (LANG_LABELS[l] ?? l)
              )}
            </button>
          ))}
        </div>
        <button
          className={copied ? "code-copy is-copied" : "code-copy"}
          onClick={copy}
          aria-label={copied ? "Copied" : `Copy ${LANG_LABELS[active]} code`}
        >
          <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            {copied ? (
              <path d="M5 12.5 10 17.5 19 7" />
            ) : (
              <>
                <rect x="8" y="8" width="12" height="12" rx="2.5" />
                <path d="M16 8V6.5A2.5 2.5 0 0 0 13.5 4h-7A2.5 2.5 0 0 0 4 6.5v7A2.5 2.5 0 0 0 6.5 16H8" />
              </>
            )}
          </svg>
          <span className="code-copy-label">{copied ? "Copied" : "Copy"}</span>
        </button>
      </div>
      <ActiveLang.Provider value={active}>{children}</ActiveLang.Provider>
    </div>
  );
}

export function CodeTab({ lang, children }: { lang: string; children: ReactNode }) {
  const active = useContext(ActiveLang);
  // Hidden tabs stay in the HTML, so search engines and no-JS readers still get all four languages.
  return (
    <div role="tabpanel" data-lang={lang} hidden={lang !== active}>
      {children}
    </div>
  );
}
