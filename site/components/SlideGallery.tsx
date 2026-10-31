"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type Props = { number: number; slides: number; video?: number; title: string };

const pad = (n: number) => String(n).padStart(2, "0");

// Swipeable carousel of the Instagram slides: /posts/NN/slide-01.png ... with the
// video slide as slide-VV.mp4, playing in place (muted, looping, inline) only while on screen.
// Its width follows the screen height (see .gallery in globals.css), so a whole slide and
// its controls always fit on one screen. Full screen uses the browser's Fullscreen API,
// or a fixed overlay where that isn't available for page elements (iPhone Safari).
export function SlideGallery({ number, slides, video, title }: Props) {
  const boxRef = useRef<HTMLElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const [current, setCurrent] = useState(0);
  const currentRef = useRef(0);
  const [nativeFull, setNativeFull] = useState(false);
  const [overlayFull, setOverlayFull] = useState(false);
  const full = nativeFull || overlayFull;
  const base = `/posts/${pad(number)}`;

  useEffect(() => {
    currentRef.current = current;
  }, [current]);

  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;
    const observer = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          const el = e.target as HTMLElement;
          if (e.isIntersecting) setCurrent(Number(el.dataset.index));
          const vid = el.querySelector("video");
          if (vid) {
            if (e.isIntersecting) vid.play().catch(() => {});
            else vid.pause();
          }
        }
      },
      { root: track, threshold: 0.6 },
    );
    track.querySelectorAll<HTMLElement>("[data-index]").forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [slides]);

  // When the track changes width (entering or leaving full screen, rotating a phone),
  // keep the same slide in view instead of landing between two slides.
  useEffect(() => {
    const track = trackRef.current;
    if (!track) return;
    const ro = new ResizeObserver(() => {
      track.scrollTo({ left: currentRef.current * track.clientWidth, behavior: "instant" });
    });
    ro.observe(track);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    const onChange = () => setNativeFull(document.fullscreenElement === boxRef.current);
    document.addEventListener("fullscreenchange", onChange);
    return () => document.removeEventListener("fullscreenchange", onChange);
  }, []);

  // Overlay mode: Esc closes it, and the page behind must not scroll.
  useEffect(() => {
    if (!overlayFull) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOverlayFull(false);
    };
    document.addEventListener("keydown", onKey);
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = overflow;
    };
  }, [overlayFull]);

  const go = useCallback(
    (index: number) => {
      const track = trackRef.current;
      if (!track) return;
      const i = Math.max(0, Math.min(slides - 1, index));
      track.scrollTo({ left: i * track.clientWidth, behavior: "smooth" });
    },
    [slides],
  );

  async function toggleFull() {
    const box = boxRef.current;
    if (!box) return;
    if (nativeFull) {
      await document.exitFullscreen().catch(() => {});
    } else if (overlayFull) {
      setOverlayFull(false);
    } else if (document.fullscreenEnabled && box.requestFullscreen) {
      await box.requestFullscreen().catch(() => setOverlayFull(true));
    } else {
      setOverlayFull(true);
    }
    trackRef.current?.focus({ preventScroll: true });
  }

  if (slides < 1) return null;

  return (
    <section
      ref={boxRef}
      className={`gallery${full ? " is-full" : ""}${overlayFull ? " is-overlay" : ""}`}
      aria-label="Slides"
      aria-roledescription="carousel"
    >
      <div
        className="gallery-track"
        ref={trackRef}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "ArrowRight") go(current + 1);
          if (e.key === "ArrowLeft") go(current - 1);
          if (e.key === "f" || e.key === "F") toggleFull();
        }}
      >
        {Array.from({ length: slides }, (_, i) => {
          const n = i + 1;
          const label = `${title}, slide ${n} of ${slides}`;
          return (
            <div className="gallery-slide" key={n} data-index={i}>
              {n === video ? (
                <video src={`${base}/slide-${pad(n)}.mp4`} muted loop playsInline preload="metadata" aria-label={label} />
              ) : (
                // eslint-disable-next-line @next/next/no-img-element -- static export: no image optimizer
                <img
                  src={`${base}/slide-${pad(n)}.png`}
                  alt={label}
                  width={1080}
                  height={1350}
                  loading={i === 0 ? "eager" : "lazy"}
                />
              )}
            </div>
          );
        })}
      </div>
      <div className="gallery-controls">
        <span className="gallery-spacer" aria-hidden="true" />
        <button onClick={() => go(current - 1)} disabled={current === 0} aria-label="Previous slide">
          ‹
        </button>
        <span className="gallery-count" aria-live="polite">
          {current + 1} / {slides}
        </span>
        <button onClick={() => go(current + 1)} disabled={current === slides - 1} aria-label="Next slide">
          ›
        </button>
        <button
          className="gallery-full"
          onClick={toggleFull}
          aria-label={full ? "Exit full screen" : "Full screen"}
          title={full ? "Exit full screen (Esc)" : "Full screen (F)"}
        >
          {full ? (
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M9 4v5H4M15 4v5h5M9 20v-5H4M15 20v-5h5" />
            </svg>
          ) : (
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" />
            </svg>
          )}
        </button>
      </div>
    </section>
  );
}
