"use client";

import { Suspense } from "react";
import dynamic from "next/dynamic";

// The player is its own chunk and each pattern is another, fetched only by
// pages that show a visualizer.
const loading = <div className="vz vz-loading">Loading the visualizer…</div>;
const Player = dynamic(() => import("./VisualizerPlayer"), { loading: () => loading });

export function VisualizerLazy(props: { patternId: string; codeHtml: string; locked?: boolean }) {
  return (
    <Suspense fallback={loading}>
      <Player {...props} />
    </Suspense>
  );
}
