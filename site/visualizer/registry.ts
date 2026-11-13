// The list of patterns, for the build (checks, pages, pseudocode colouring).
// To add a pattern: write patterns/<id>.ts, add it here and in loaders.ts
// (how the browser fetches it), add post-kit/viz/<id>/ref.py, and run
// `npm run viz-fixtures`.
import type { Pattern } from "./schema.ts";
import { binarySearch } from "./patterns/binary-search.ts";
import { monotonicStack } from "./patterns/monotonic-stack.ts";
import { slidingWindow } from "./patterns/sliding-window.ts";
import { twoPointers } from "./patterns/two-pointers.ts";

export const patterns: Pattern[] = [twoPointers, slidingWindow, binarySearch, monotonicStack];

export function patternById(id: string): Pattern | undefined {
  return patterns.find((p) => p.id === id);
}
