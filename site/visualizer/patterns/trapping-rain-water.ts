// Trapping rain water: two pointers, each remembering the tallest wall behind it (LeetCode 42, post 18).
import type { Answer, Input, Pattern, Step } from "../schema.ts";
import { varOf } from "../schema.ts";
import { list, pick, ptrs, sayOk, step, sum } from "./_lib.ts";

const pseudocode = [
  "function trap(height):",
  "    left = 0",
  "    right = length(height) - 1",
  "    leftMax = 0                // tallest wall seen",
  "    rightMax = 0",
  "    water = 0",
  "    while left < right:",
  "        if height[left] < height[right]:",
  "            bar = height[left]",
  "            leftMax = max(leftMax, bar)",
  "            water = water + leftMax - bar",
  "            left = left + 1",
  "        else:",
  "            bar = height[right]",
  "            rightMax = max(rightMax, bar)",
  "            water = water + rightMax - bar",
  "            right = right - 1",
  "    return water",
];

function* run(input: Input): Generator<Step, Answer, void> {
  const h = input.height as number[];
  const n = h.length;
  const held: number[] = Array(n).fill(0); // water standing on each bar so far
  let left = 0, right = n - 1, leftMax = 0, rightMax = 0, water = 0;
  const snap = (line: number, say: string, focus = -1) =>
    step(
      line,
      say,
      [
        {
          kind: "bars",
          id: "height",
          bars: h.map((x, i) => ({ id: `b${i}`, h: x, water: held[i], state: i === focus ? "gold" : i < left || i > right ? "dim" : "plain" })),
          pointers: left === right ? [{ id: "left", label: "met", at: left }] : ptrs(n, { left, right }),
        },
      ],
      { leftMax, rightMax, water },
    );

  yield snap(5, "left and right start on the two ends. Each remembers the tallest wall it has passed.");
  while (left < right) {
    if (h[left] < h[right]) {
      const bar = h[left];
      leftMax = Math.max(leftMax, bar);
      held[left] = leftMax - bar;
      water += held[left];
      left++;
      yield snap(11, held[left - 1] ? `The left bar ${bar} is below the left wall ${leftMax}: it holds ${held[left - 1]}. water = ${water}.` : `The left bar ${bar} is the tallest on its side so far: it holds nothing.`, left - 1);
    } else {
      const bar = h[right];
      rightMax = Math.max(rightMax, bar);
      held[right] = rightMax - bar;
      water += held[right];
      right--;
      yield snap(16, held[right + 1] ? `The right bar ${bar} is below the right wall ${rightMax}: it holds ${held[right + 1]}. water = ${water}.` : `The right bar ${bar} is the tallest on its side so far: it holds nothing.`, right + 1);
    }
  }
  yield snap(17, `left and right have met. The bars hold ${water} units of water.`);
  return water;
}

function check(input: Input, s: Step, prev: Step | null, isLast: boolean): string | null {
  const h = input.height as number[];
  const b = s.views[0];
  if (s.views.length !== 1 || b.kind !== "bars") return "needs exactly the bars view";
  if (b.bars.some((x, i) => x.h !== h[i])) return "the bars must be the input";
  const at = (id: string) => b.pointers.find((p) => p.id === id)?.at;
  const left = at("left")!;
  const right = at("right") ?? left;
  if (left === undefined || left > right) return "left must not pass right";
  for (const [i, x] of b.bars.entries()) {
    // A bar the pointers have passed holds what the tallest walls on its two sides allow.
    const level = Math.min(Math.max(...h.slice(0, i + 1)), Math.max(...h.slice(i)));
    if (x.water !== (i < left || i > right ? level - h[i] : 0)) return `bar ${i} shows ${x.water} of water`;
  }
  if (varOf(s, "water") !== sum(b.bars.map((x) => x.water))) return "water is not the sum of the water on the bars";
  if (varOf(s, "leftMax") !== Math.max(0, ...h.slice(0, left)) || varOf(s, "rightMax") !== Math.max(0, ...h.slice(right + 1))) return "leftMax and rightMax must be the tallest bars passed";
  if (isLast !== (s.line === 17) || (isLast && left !== right)) return "the trace must end on 'return water', when the pointers meet";
  return sayOk(input, s, prev);
}

export const trappingRainWater: Pattern = {
  id: "trapping-rain-water",
  title: "Trapping rain water",
  blurb: "Water above a bar depends on the tallest wall on each side: two pointers find it in one pass.",
  problem: "Count the units of rain the bars trap between them.",
  section: "Arrays and hashing",
  tier: "paid",
  post: "trapping-rain-water",
  pseudocode,
  fields: [{ name: "height", label: "Bar heights", kind: "ints", min: 0, max: 9, minLen: 1, maxLen: 10 }],
  example: { height: [2, 0, 3, 1, 0, 2, 1, 2] },
  validate: () => null,
  random: (rng) => ({ height: list(rng, pick(rng, 6, 9), 0, 5) }),
  run,
  check,
  sameAnswer: (_i, got, expected) => got === expected,
  answerText: (a) => `Units of water trapped: ${a}`,
};
