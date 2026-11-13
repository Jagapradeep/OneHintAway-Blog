// How the browser fetches a pattern: one chunk per pattern, loaded only when a
// player asks for it. (registry.ts imports every pattern at once and is for the
// build: the checks, the pages' text and the pseudocode colouring.)
//
// When the paywall arrives, paid patterns' chunks are what moves behind the
// server check; nothing else here needs to change. Keep the keys equal to the
// ids in registry.ts: the build check compares them.
import type { Pattern } from "./schema.ts";

export const loaders: Record<string, () => Promise<Pattern>> = {
  "hash-two-sum": () => import("./patterns/hash-two-sum.ts").then((m) => m.hashTwoSum),
  "two-pointers": () => import("./patterns/two-pointers.ts").then((m) => m.twoPointers),
  "fixed-window": () => import("./patterns/fixed-window.ts").then((m) => m.fixedWindow),
  "sliding-window": () => import("./patterns/sliding-window.ts").then((m) => m.slidingWindow),
  "min-window": () => import("./patterns/min-window.ts").then((m) => m.minWindow),
  "prefix-sum": () => import("./patterns/prefix-sum.ts").then((m) => m.prefixSum),
  "prefix-sum-hash-map": () => import("./patterns/prefix-sum-hash-map.ts").then((m) => m.prefixSumHashMap),
  "kadane": () => import("./patterns/kadane.ts").then((m) => m.kadane),
  "three-way-partition": () => import("./patterns/three-way-partition.ts").then((m) => m.threeWayPartition),
  "moores-voting": () => import("./patterns/moores-voting.ts").then((m) => m.mooresVoting),
  "cyclic-sort": () => import("./patterns/cyclic-sort.ts").then((m) => m.cyclicSort),
  "next-permutation": () => import("./patterns/next-permutation.ts").then((m) => m.nextPermutation),
  "trapping-rain-water": () => import("./patterns/trapping-rain-water.ts").then((m) => m.trappingRainWater),
  "recursion": () => import("./patterns/recursion.ts").then((m) => m.recursion),
  "insertion-sort": () => import("./patterns/insertion-sort.ts").then((m) => m.insertionSort),
  "selection-sort": () => import("./patterns/selection-sort.ts").then((m) => m.selectionSort),
  "bubble-sort": () => import("./patterns/bubble-sort.ts").then((m) => m.bubbleSort),
  "merge-sort": () => import("./patterns/merge-sort.ts").then((m) => m.mergeSort),
  "quick-sort": () => import("./patterns/quick-sort.ts").then((m) => m.quickSort),
  "binary-search": () => import("./patterns/binary-search.ts").then((m) => m.binarySearch),
  "lower-bound": () => import("./patterns/lower-bound.ts").then((m) => m.lowerBound),
  "rotated-sorted-array": () => import("./patterns/rotated-sorted-array.ts").then((m) => m.rotatedSortedArray),
  "search-2d-matrix": () => import("./patterns/search-2d-matrix.ts").then((m) => m.search2dMatrix),
  "binary-search-on-answers": () => import("./patterns/binary-search-on-answers.ts").then((m) => m.binarySearchOnAnswers),
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
