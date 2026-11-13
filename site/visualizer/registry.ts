// The list of patterns, for the build (checks, pages, pseudocode colouring).
// To add a pattern: write patterns/<id>.ts, add it here and in loaders.ts
// (how the browser fetches it), add post-kit/viz/<id>/ref.py, and run
// `npm run viz-fixtures`.
import type { Pattern } from "./schema.ts";
import { binarySearch } from "./patterns/binary-search.ts";
import { binarySearchOnAnswers } from "./patterns/binary-search-on-answers.ts";
import { bubbleSort } from "./patterns/bubble-sort.ts";
import { cyclicSort } from "./patterns/cyclic-sort.ts";
import { fixedWindow } from "./patterns/fixed-window.ts";
import { hashTwoSum } from "./patterns/hash-two-sum.ts";
import { insertionSort } from "./patterns/insertion-sort.ts";
import { kadane } from "./patterns/kadane.ts";
import { lowerBound } from "./patterns/lower-bound.ts";
import { mergeSort } from "./patterns/merge-sort.ts";
import { minWindow } from "./patterns/min-window.ts";
import { monotonicStack } from "./patterns/monotonic-stack.ts";
import { mooresVoting } from "./patterns/moores-voting.ts";
import { nextPermutation } from "./patterns/next-permutation.ts";
import { prefixSum } from "./patterns/prefix-sum.ts";
import { prefixSumHashMap } from "./patterns/prefix-sum-hash-map.ts";
import { quickSort } from "./patterns/quick-sort.ts";
import { recursion } from "./patterns/recursion.ts";
import { rotatedSortedArray } from "./patterns/rotated-sorted-array.ts";
import { search2dMatrix } from "./patterns/search-2d-matrix.ts";
import { selectionSort } from "./patterns/selection-sort.ts";
import { slidingWindow } from "./patterns/sliding-window.ts";
import { threeWayPartition } from "./patterns/three-way-partition.ts";
import { trappingRainWater } from "./patterns/trapping-rain-water.ts";
import { twoPointers } from "./patterns/two-pointers.ts";

// The gallery shows them in this order inside each roadmap section.
export const patterns: Pattern[] = [
  hashTwoSum,
  twoPointers,
  fixedWindow,
  slidingWindow,
  minWindow,
  prefixSum,
  prefixSumHashMap,
  kadane,
  threeWayPartition,
  mooresVoting,
  cyclicSort,
  nextPermutation,
  trappingRainWater,
  recursion,
  insertionSort,
  selectionSort,
  bubbleSort,
  mergeSort,
  quickSort,
  binarySearch,
  lowerBound,
  rotatedSortedArray,
  search2dMatrix,
  binarySearchOnAnswers,
  monotonicStack,
];

export function patternById(id: string): Pattern | undefined {
  return patterns.find((p) => p.id === id);
}
