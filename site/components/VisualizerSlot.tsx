"use client";

import { lazy, Suspense, type ComponentProps } from "react";

// What the post page imports. Every post page carries this file, so it stays a
// few hundred bytes: the sign-in gate and the player are their own chunks,
// fetched only by pages that show a visualizer. (The static build waits for
// them, so a page's HTML is the same as when they were imported directly.)
const Gate = lazy(() => import("./VisualizerGate").then((m) => ({ default: m.VisualizerGate })));
const Player = lazy(() => import("./VisualizerLazy").then((m) => ({ default: m.VisualizerLazy })));

/** Pass `gate` (accounts on: the sign-in gate decides) or `player` (accounts off). */
export function VisualizerSlot({ gate, player }: { gate?: ComponentProps<typeof Gate>; player?: ComponentProps<typeof Player> }) {
  return (
    <Suspense fallback={<div className="vz vz-loading">Loading the visualizer…</div>}>
      {gate ? <Gate {...gate} /> : player ? <Player {...player} /> : null}
    </Suspense>
  );
}
