"use client";

import { lazy, Suspense } from "react";

// The player is its own chunk and each pattern is another, fetched only by
// pages that show a visualizer. React.lazy, not next/dynamic: it adds no
// runtime of its own to the pages that import this file.
const loading = <div className="vz vz-loading">Loading the visualizer…</div>;
const Player = lazy(() => import("./VisualizerPlayer"));

export function VisualizerLazy(props: { patternId: string; codeHtml: string; locked?: boolean }) {
  return (
    <Suspense fallback={loading}>
      <Player {...props} />
    </Suspense>
  );
}
