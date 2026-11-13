// How the browser fetches a pattern: one chunk per pattern, loaded only when a
// player asks for it. (registry.ts imports every pattern at once and is for the
// build: the checks, the pages' text and the pseudocode colouring.)
//
// When the paywall arrives, paid patterns' chunks are what moves behind the
// server check; nothing else here needs to change. Keep the keys equal to the
// ids in registry.ts: the build check compares them.
import type { Pattern } from "./schema.ts";

export const loaders: Record<string, () => Promise<Pattern>> = {
  "two-pointers": () => import("./patterns/two-pointers.ts").then((m) => m.twoPointers),
  "binary-search": () => import("./patterns/binary-search.ts").then((m) => m.binarySearch),
  "sliding-window": () => import("./patterns/sliding-window.ts").then((m) => m.slidingWindow),
  "monotonic-stack": () => import("./patterns/monotonic-stack.ts").then((m) => m.monotonicStack),
};

const loading = new Map<string, Promise<Pattern>>();

/** The same promise every time for one id, so React's use() can wait on it. */
export function loadPattern(id: string): Promise<Pattern> {
  let p = loading.get(id);
  if (!p) {
    const load = loaders[id];
    p = load ? load() : Promise.reject(new Error(`No visualizer pattern "${id}"`));
    loading.set(id, p);
  }
  return p;
}
