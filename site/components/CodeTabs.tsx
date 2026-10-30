"use client";

import { createContext, useContext, useRef, useState, useSyncExternalStore, type ReactNode } from "react";

export const LANG_LABELS: Record<string, string> = {
  java: "Java",
  python: "Python",
  cpp: "C++",
  javascript: "JavaScript",
};
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
      <div className="code-tabs-bar" role="tablist">
        {available.map((l) => (
          <button
            key={l}
            role="tab"
            aria-selected={l === active}
            className={l === active ? "active" : undefined}
            onClick={() => writeLang(l)}
          >
            {LANG_LABELS[l] ?? l}
          </button>
        ))}
        <button className="code-copy" onClick={copy} aria-label={`Copy ${LANG_LABELS[active]} code`}>
          {copied ? "Copied" : "Copy"}
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
