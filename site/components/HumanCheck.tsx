"use client";

import { useEffect, useRef } from "react";
import { TURNSTILE_SITE_KEY } from "@/lib/site";

// Cloudflare Turnstile: "is a person using this form, or a script?" Every sign-in code costs
// a real email, so the API emails one only with a token from this check (it verifies the
// token with Cloudflare using a secret key the site never sees).
//
// Most readers never see anything: the check runs in the background while they type their
// email ("interaction-only"). Only a browser Cloudflare is unsure about gets a checkbox.
// Cloudflare's script is loaded only when a sign-in form is on screen, never on other pages.
// Without NEXT_PUBLIC_TURNSTILE_SITE_KEY (your laptop) none of this runs.

type Turnstile = {
  render(el: HTMLElement, options: Record<string, unknown>): string;
  reset(id: string): void;
  remove(id: string): void;
};

declare global {
  interface Window {
    turnstile?: Turnstile;
  }
}

const SCRIPT = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
const WAIT_MS = 15000;

let loading: Promise<Turnstile> | null = null;

function loadTurnstile(): Promise<Turnstile> {
  if (window.turnstile) return Promise.resolve(window.turnstile);
  loading ??= new Promise<Turnstile>((resolve, reject) => {
    const script = document.createElement("script");
    script.src = SCRIPT;
    script.async = true;
    script.onload = () => (window.turnstile ? resolve(window.turnstile) : reject(new Error("no turnstile")));
    script.onerror = () => {
      loading = null; // blocked or offline: try again next time a form opens
      script.remove();
      reject(new Error("turnstile blocked"));
    };
    document.head.appendChild(script);
  });
  return loading;
}

export type HumanCheck = {
  // Where the widget goes (it stays empty unless Cloudflare needs the reader to click).
  boxRef: React.RefObject<HTMLDivElement | null>;
  // A fresh token for one request. Neither field = no check configured (send no token).
  // problem "click": Cloudflare showed a checkbox the reader hasn't ticked yet.
  // problem "failed": the check couldn't be done (script blocked, Cloudflare unreachable,
  // Cloudflare refused this browser, or it took too long).
  token(): Promise<HumanToken>;
};

export type HumanToken = { token?: string; problem?: "click" | "failed" };

export function useHumanCheck(): HumanCheck {
  const boxRef = useRef<HTMLDivElement | null>(null);
  const widget = useRef<string | null>(null);
  const ready = useRef<string | null>(null); // a token not yet used
  const waiting = useRef<((token: string | null) => void)[]>([]);
  const needsClick = useRef(false); // Cloudflare is showing a checkbox

  useEffect(() => {
    const el = boxRef.current;
    if (!TURNSTILE_SITE_KEY || !el) return;
    let gone = false;
    const hand = (token: string | null) => {
      const list = waiting.current;
      waiting.current = [];
      if (list.length && token) {
        list[0](token); // a token works once: the first request gets it, the rest fail
        list.slice(1).forEach((fn) => fn(null));
      } else if (list.length) list.forEach((fn) => fn(null));
      else ready.current = token;
    };
    loadTurnstile()
      .then((ts) => {
        if (gone) return;
        widget.current = ts.render(el, {
          sitekey: TURNSTILE_SITE_KEY,
          action: "sign-in",
          appearance: "interaction-only",
          size: "flexible",
          theme: document.documentElement.dataset.theme === "light" ? "light" : "dark",
          callback: (token: string) => {
            needsClick.current = false;
            hand(token);
          },
          "before-interactive-callback": () => {
            needsClick.current = true;
            hand(null); // a request waiting for a token gets "tick the box" now, not in 15 s
          },
          "expired-callback": () => {
            ready.current = null; // Turnstile fetches a new one by itself
          },
          "error-callback": () => {
            ready.current = null;
            hand(null);
          },
        });
      })
      .catch(() => {
        if (!gone) hand(null);
      });
    return () => {
      gone = true;
      if (widget.current) window.turnstile?.remove(widget.current);
      widget.current = null;
      ready.current = null;
      needsClick.current = false;
      waiting.current.forEach((fn) => fn(null));
      waiting.current = [];
    };
  }, []);

  function token(): Promise<HumanToken> {
    if (!TURNSTILE_SITE_KEY) return Promise.resolve({});
    const take = (t: string): HumanToken => {
      // Spent by this request: ask Turnstile for the next one straight away.
      if (widget.current) window.turnstile?.reset(widget.current);
      return { token: t };
    };
    const missing = (): HumanToken => ({ problem: needsClick.current ? "click" : "failed" });
    if (ready.current) {
      const t = ready.current;
      ready.current = null;
      return Promise.resolve(take(t));
    }
    if (needsClick.current) return Promise.resolve(missing());
    return new Promise((resolve) => {
      const timer = window.setTimeout(() => {
        waiting.current = waiting.current.filter((fn) => fn !== done);
        resolve(missing());
      }, WAIT_MS);
      function done(t: string | null) {
        window.clearTimeout(timer);
        resolve(t ? take(t) : missing());
      }
      waiting.current.push(done);
    });
  }

  return { boxRef, token };
}
