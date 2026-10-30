"use client";

import { useEffect, useRef, useState } from "react";

type Props = { number: number; slides: number; video?: number; title: string };

const pad = (n: number) => String(n).padStart(2, "0");

// Swipeable carousel of the Instagram slides: /posts/NN/slide-01.png ... with the
// video slide as slide-VV.mp4, playing in place (muted, looping, inline) only while on screen.
export function SlideGallery({ number, slides, video, title }: Props) {
  const trackRef = useRef<HTMLDivElement>(null);
  const [current, setCurrent] = useState(0);
  const base = `/posts/${pad(number)}`;

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

  function go(index: number) {
    const track = trackRef.current;
    if (!track) return;
    const i = Math.max(0, Math.min(slides - 1, index));
    track.scrollTo({ left: i * track.clientWidth, behavior: "smooth" });
  }

  if (slides < 1) return null;

  return (
    <section className="gallery" aria-label="Slides" aria-roledescription="carousel">
      <div
        className="gallery-track"
        ref={trackRef}
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "ArrowRight") go(current + 1);
          if (e.key === "ArrowLeft") go(current - 1);
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
        <button onClick={() => go(current - 1)} disabled={current === 0} aria-label="Previous slide">
          ‹
        </button>
        <span aria-live="polite">
          {current + 1} / {slides}
        </span>
        <button onClick={() => go(current + 1)} disabled={current === slides - 1} aria-label="Next slide">
          ›
        </button>
      </div>
    </section>
  );
}
