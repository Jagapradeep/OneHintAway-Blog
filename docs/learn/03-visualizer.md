# 3 · The visualizer

> ⏱ 45 min · 🧰 `site/` installed · No API needed

## 📖 The story

There are 35 patterns in the visualizer, each one a small algorithm that animates on the
reader's own input. Every build runs each of them against a **brute-force answer** on 42,189
test inputs, and checks **every single step** against a rule book. If a pattern lies on even
one step of one input, the site doesn't deploy.

That sounds like overkill until you remember what the site is for: teaching. A visualizer that
animates a wrong step teaches the wrong thing. So the question of this chapter is: **how do you
test an animation?**

## 💡 The idea in 2 minutes

The trick is that **the animation isn't the program**. The program is a JavaScript *generator*
that records what the algorithm is doing, step by step, as plain data. The player only draws
that data.

```ts
// site/visualizer/patterns/two-pointers.ts (shortened)
function* run(input) {
  let left = 0, right = nums.length - 1;
  yield snap(L_START, "left starts on the first number, right on the last.");
  while (left < right) {
    const total = nums[left] + nums[right];
    yield snap(L_TOTAL, `Add the two ends: ${nums[left]} + ${nums[right]} = ${total}.`);
    if (total === target) return [left + 1, right + 1];       // the answer
    if (total < target) left++; else right--;
    yield snap(...);                                           // "too small, so left moves in"
  }
}
```

`function*` makes a generator: each `yield` hands out one **step**, and `return` gives the
answer. A step is a full snapshot, never a change:

```text
Step = {
  line:  4,                                     ← which pseudocode line is running (gold bar)
  say:   "Add the two ends: 1 + 11 = 12.",      ← the narration (at most 110 characters)
  views: [ { kind: "array", id: "numbers",      ← what to draw: arrays, stacks, trees, maps,
             cells: [...], pointers: [...] } ],    grids, bars, linked lists
  vars:  [ { name: "total", value: 12 } ]
}
```

Because steps are data, they can be **tested like data**:

| Check | Catches |
| --- | --- |
| The answer vs a brute force (from `post-kit/viz/<id>/ref.py`, saved as `visualizer/fixtures/<id>.json`) | a wrong algorithm |
| The schema's generic rules (`schema.ts`: cell ids unique, pointers in bounds, …) | a malformed picture |
| The pattern's own `check()`, written separately from `run()` | a step that misdescribes what happened ("only left may move, one step right") |
| The pseudocode vs the post's `## Pseudocode` block | the player and the post telling different stories |
| 500 random inputs per pattern | cases nobody thought of |

All of this runs in `npm run check-viz`, which runs before every build (`prebuild`).

## 📂 Where it lives

| File | Role |
| --- | --- |
| `site/visualizer/schema.ts` | the step and view types, and the generic checks |
| `site/visualizer/patterns/<id>.ts` | one pattern: `run` (generator), `check`, `validate`, `random`, `example`, pseudocode |
| `site/visualizer/patterns/_lib.ts` | shared helpers (`tiles`, `ptrs`, `swap`, …) |
| `site/visualizer/registry.ts` | the list of patterns; `loaders.ts`: one browser chunk per pattern |
| `site/visualizer/access.ts` | free / paid tiers, and `canPlay()`: the sign-in gate |
| `site/scripts/check-visualizer.mjs` | the build check (Node runs the TypeScript directly with `--experimental-strip-types`) |
| `post-kit/viz/<id>/ref.py`, `post-kit/tools/viz_fixtures.py` | the Python brute force that writes the fixtures |
| `site/components/VisualizerPlayer.tsx`, `views/*.tsx` | the player: play, step, scrub, keyboard; one component per view kind |

**How the player draws motion.** Each cell has a stable `id`. When a step swaps two cells, the
player keeps the DOM order fixed and moves cells with
`transform: translateX(calc(var(--at) * 100%))`, so a swap *slides* instead of jumping.
Transforms and opacity are cheap for the browser to animate, even on phones.
`prefers-reduced-motion` switches the motion off.

## 🛠 Try it (20 min)

**1. Play it.** `npm run dev`, open http://localhost:3000/visualize/two-pointers/, type your own
numbers, press Run. Use the arrow keys to step. Watch the gold bar move through the pseudocode.

**2. Run the generator by hand.** This prints the steps the player would draw, with no browser
(from `site/`):

```bash
node --experimental-strip-types ../docs/learn/try/steps.mjs                 # list every pattern id
node --experimental-strip-types ../docs/learn/try/steps.mjs two-pointers    # the example
node --experimental-strip-types ../docs/learn/try/steps.mjs two-pointers '{"numbers":[2,7,11,15],"target":9}'
node --experimental-strip-types ../docs/learn/try/steps.mjs kadane
```

Read the output beside `visualizer/patterns/two-pointers.ts`: every printed line is one `yield`.

**3. The quick build check.**

```bash
npm run check-viz -- --sample 50       # 50 inputs per pattern instead of all; a few seconds
```

## 💥 Break it (10 min)

In `visualizer/patterns/two-pointers.ts`, find `left = left + 1;` and make it `left = left + 2;`.
Run the quick check again:

```text
check-visualizer: 5 problem(s)
  two-pointers: example: step 5 of 9: only left may move, one step right
      narration: "9 is less than 10: too small, so left moves one step in."
```

The pattern's own `check()` caught a step that lied: the narration says "one step", the picture
moved two. Run the helper from step 2 to see the steps go wrong. Then undo:
`git checkout -- visualizer/patterns/two-pointers.ts`.

## 🧠 Explain it

<details>
<summary>1. Why is `run` a generator instead of a function that returns an array of steps?</summary>

The algorithm reads like the normal algorithm, with a `yield` wherever something worth showing
happens. The generator pauses there, so the code doesn't have to build and manage a list by
hand, and the answer is the generator's `return` value. Collecting the steps into an array is
one loop (see `docs/learn/try/steps.mjs`).
</details>

<details>
<summary>2. Why is every step a full snapshot and not "what changed"?</summary>

The reader can scrub to any step or step backwards. With full snapshots, step 37 is just
`steps[36]`: no replaying from the start, and no chance of drift. It also makes each step
testable on its own.
</details>

<details>
<summary>3. Why is `check()` written separately from `run()`?</summary>

If the same code produced and judged a step, a bug would agree with itself. `check()` restates
the rules independently ("only left may move, one step right"), like a second person reviewing.
That's how it caught the `left + 2` bug while the final answer was still often right.
</details>

<details>
<summary>4. The brute force is in Python but the patterns are TypeScript. Why?</summary>

Two independent implementations in two languages are unlikely to share a bug. Python writes the
answers to committed JSON fixtures, so the cloud build never needs Python: Node only compares.
</details>

<details>
<summary>5. Does the sign-in gate protect the visualizer's code?</summary>

No. The pattern chunks are public static files. The gate is a sign-up incentive, not access
control: real protection would need a server check before serving paid chunks (not built yet).
</details>

## 🎤 Interview corner

> "How would you test something visual?" Separate the logic from the drawing: make the logic
> produce plain data, then test that data against an independent reference (a brute force) and
> an independent rule set, on thousands of generated inputs. The drawing layer stays thin and is
> checked by a few browser tests.

## ✅ You now know

- [ ] What a step is, and why it's a snapshot
- [ ] How a generator turns an algorithm into a list of steps
- [ ] The five checks that run before every build
- [ ] Why the gate is not security

---

**Next →** [4 · How a post reaches the site](04-content-pipeline.md)
