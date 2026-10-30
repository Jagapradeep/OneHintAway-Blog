// Roadmap sections in reading order (from the dsa-post skill's roadmap).
// A post's `section` must match one of these (case doesn't matter);
// anything else is listed after them so a typo never hides a post.
export const SECTIONS = [
  "Start here",
  "Foundations",
  "Arrays and hashing",
  "Maths",
  "Recursion and sorting",
  "Binary search",
  "2D arrays and strings",
  "Backtracking",
  "Linked list",
  "Bit manipulation",
  "Greedy",
  "Stack and queue",
  "Trees",
  "Heaps",
  "Graphs",
  "Dynamic programming",
  "Tries and strings",
  "Advanced (optional)",
];

export function sectionIndex(section: string): number {
  const i = SECTIONS.findIndex((s) => s.toLowerCase() === section.toLowerCase());
  return i === -1 ? SECTIONS.length : i;
}

export const slugify = (s: string) =>
  s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
