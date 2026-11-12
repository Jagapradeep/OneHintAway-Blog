# One Hint Away post kit

Turns one small content file into a finished carousel: slides, the motion video, PNGs, the blog page and a plain-text review summary. Claude writes **content only**; every layout, colour, header, footer, counter and number comes from here.

```
post-kit/
  render.py            the one command
  kit/ui.py            Graphite & Chrome v3.1 pieces (copied from posts 22 and 18)
  kit/post.py          templates, derived values, validator, summary
  kit/video.py         generic motion slide (timeline + player + MP4)
  kit/blog.py          blog MDX and the four-language tests
  fonts/               Sora, Manrope, Geist Mono (SIL OFL), embedded into every render
  tools/deband.py      final-export banding fix
  tools/check_mdx.mjs  blog page check (npm install in tools/ first)
  posts/NN-slug/       post.json (content), ref.py (reference code: every number comes from it),
                       code/ (Java, Python, C++, JavaScript), blog.md (blog body)
  used_problems.json   practice problems already used, by post number
  viz/<pattern>/ref.py reference code for the website's interactive visualizer (last section)
  tools/viz_fixtures.py  writes the visualizer's test files into site/visualizer/fixtures/
```

## Run the build yourself, step by step

Use **WSL (Ubuntu)** on Windows, or any Linux or macOS shell. The kit calls `python3`, runs `./a.out` and chains commands with `&&`, which plain Windows cmd and PowerShell don't support.

### 1. One-time setup

1. Install WSL with Ubuntu (Windows only), from PowerShell as admin:
   ```
   wsl --install -d Ubuntu
   ```
   Restart, open **Ubuntu**, and do everything below inside it.
2. Install the system tools:
   ```
   sudo apt update
   sudo apt install -y python3 python3-pip ffmpeg nodejs npm default-jdk g++ git
   ```
   `ffmpeg` makes the video. `nodejs` runs the blog page check and the JavaScript tests. The JDK and `g++` are only needed for `--test`, which compiles the Java and C++ code.
3. Install the Python packages and the browser the kit renders with:
   ```
   python3 -m pip install --break-system-packages playwright pillow numpy scipy opencv-python-headless fonttools brotli
   python3 -m playwright install --with-deps chromium
   ```
   `numpy`, `scipy` and `opencv-python-headless` run the final-export banding fix (`tools/deband.py`). `fonttools` and `brotli` let the kit measure cover titles in the real Sora font so they stay on one line. Without them it still renders, and the layout check still guards.
4. Get the repo (or use your existing clone from inside WSL, e.g. `/mnt/c/Users/<you>/...`):
   ```
   git clone https://github.com/Jagapradeep/OneHintAway-Blog
   cd OneHintAway-Blog
   ```
5. Install the blog page check's packages (once, and again if `tools/package.json` changes):
   ```
   (cd post-kit/tools && npm install)
   ```

### 2. Check a post (fast, about a minute)

From the repo root:

```
python3 post-kit/render.py post-kit/posts/24-bubble-sort --test --png review
```

- `--test` runs the post's code in Java, Python, C++ and JavaScript on 1,000+ inputs against `ref.py`.
- `--png review` renders small PNGs into `build/24-bubble-sort/png/` so you can look at every slide.
- It ends with `OK ...` or with `VALIDATION FAILED` / `LAYOUT FAILED` and the exact slide and reason. Fix `post.json` and run again.

### 3. Export the finished zip

```
python3 post-kit/render.py post-kit/posts/24-bubble-sort --export --start 2026-11-09
```

The zip lands in `build/24-bubble-sort.zip`: `slide-NN.png`, the `slide-02.mp4` video, `NN-slug.mdx` (blog page), `caption.txt` and `alt-text.txt`. It takes 1 to 3 minutes per post, mostly the video. `--export` always runs the tests and stops on any layout problem.

### 4. Posting dates

`--start` is the posting date of the **first** post in that run. It goes into the blog page.

```
# a batch, one post every weekday from Mon 9 Nov
python3 post-kit/render.py post-kit/posts/2[4-9]-* post-kit/posts/3[0-2]-* --export --start 2026-11-09

# a batch, one post every day (weekends too) from Sat 7 Nov
python3 post-kit/render.py post-kit/posts/2[4-9]-* post-kit/posts/3[0-2]-* --export --start 2026-11-07 --daily

# one post on its own: give its own date
python3 post-kit/render.py post-kit/posts/27-reverse-pairs --export --start 2026-11-12
```

Posts are dated in folder order, so re-exporting one post from a batch needs that post's own date.

### 5. Post it

1. Unzip the day's zip.
2. Instagram: upload the slides in number order as one carousel, with `slide-02.mp4` in place of slide 2. Paste `caption.txt`. Add each slide's alt text from `alt-text.txt` under Advanced settings → Accessibility.
3. Blog: from the blog project, run `npm run add-post -- NN-slug/NN-slug.mdx NN-slug/`, then commit and deploy as usual.

### If something fails

| You see | Why | Fix |
| --- | --- | --- |
| `PermissionError: Operation not permitted` on a copy | Old kit on a Windows folder (`/mnt/c`), where WSL can't change file permissions | Use this kit (it copies contents only), or move the repo into WSL (below) |
| `deband.py failed ... No module named 'cv2'` | The banding fix needs OpenCV | `python3 -m pip install --break-system-packages opencv-python-headless numpy scipy pillow` |
| `VALIDATION FAILED` / `LAYOUT FAILED` | A rule or the fixed frame was broken; the slide and reason are printed | A too-long line is usually a one-word cut in `post.json`; numbers or code go back to Claude |

Always install with `python3 -m pip`, so packages go into the same Python the kit runs with.

**Keep the repo on WSL's own disk.** It works under `/mnt/c`, but every PNG and video frame then goes through the slow Windows file bridge. Copy it once and run from there:

```
cp -r /mnt/c/DSA-Post/OneHintAway-Blog ~/OneHintAway-Blog
cd ~/OneHintAway-Blog
```

The zips are then at `\\wsl$\Ubuntu\home\<you>\OneHintAway-Blog\build` in Windows Explorer.

### Other flags

| Flag | What it does |
| --- | --- |
| *(none)* | Check the post and write `build/NN-slug/project/` and `summary.txt` |
| `--png review` / `--png final` | Small or full-size PNGs |
| `--video draft` / `--video final` | Just the video |
| `--test` | Four-language tests |
| `--export` | Everything above, final quality, zipped |
| `--start YYYY-MM-DD` | First posting date |
| `--daily` | With `--start`: next calendar days instead of next weekdays |
| `--out DIR` | Write to `DIR` instead of `./build` |
| `--force` | Render even when validation or layout fails (to look, never to post) |

## Templates

- **concept** (8 slides, like posts 20–22): cover, video, story, picture + quick check, extra (opens with the quick-check answer, then one more idea on the post's own numbers), template, trap + cost, practice. A post with a second, bigger idea may add one more `extra` slide.
- **challenge** (13 slides): cover, story, problem, pause, 4 hints (3–5 allowed), bridge, video, 2 solution slides (1–2 allowed), closing.

## What is derived (cannot be typed wrong)

Slide counter, progress bar, header, footer, footer teasers (each slide's `teaser` shows on the slide before it), "BY SLIDE N", "in N lines", read time, answer banner after a quick check, hint and solution labels, solution line numbers, the bridge's "next N slides", the closing AI prompt, the blog line, cover title size, every `{{expression}}` (computed by `ref.py`), every posting date, and every number in the video.

## Fixed frame

Every slide is 1080 × 1350. The header (logo, slide count, progress bar) sits at the top and the footer (@onehintaway and the next-slide pill) is pinned 64 px from the bottom with 80 px side margins, on every slide and in the video. Content can never move them; if content runs into either, the render fails.

Fonts are embedded into each render as data, so PNGs and MP4s always use Sora, Manrope and Geist Mono, the same as the designs. Paragraphs avoid one-word last lines, two-line titles split evenly, and short maths such as `n − 1` or `2 × r` never breaks across lines.

## What the validator refuses

- Wrong slide order or count for the template
- A story without a `scene`
- A quick check whose answer doesn't match `ref.py`
- A cost that isn't Big-O
- An example whose output doesn't match
- A practice hint too slow for the problem's limits (complexity at max input > 10⁸, unless marked `partial`). It checks the `complexity` you declare, not the note's wording, so make the two agree.
- `dash` on a box that holds a value. `dash` draws an empty dashed slot (a gap); mark values with `gold` (current pick), `steel` (done, or compared against the gold one) or `dim` (out of play).
- Banned hook words; teasers over 34 characters

Layout check after rendering: anything running into the header or footer, text cut off, text leaving the side margins.

## Video

Steps describe states (`swap`, `move`, `set`, `gold`, `steel`, `frame`, `band`, `ptr`, `water`, `eq`, `chip`, `caption`); `ref.py` usually generates them by running the real algorithm. Two stages: `boxes` (arrays) and `bars` (heights and water). Each step's caption and equation change as the boxes start to move, and the result and chip land as the boxes arrive. Give a step a `chip` only when it says something new (like `sweep 1: 4` or `3 → slot 2`). Frames that don't change are reused, not re-rendered (about 40% of a typical video).

## Website visualizer, step by step

The blog has an interactive player where a reader steps through a pattern on their own numbers: at `/visualize/` (a gallery, with one page per pattern at `/visualize/<pattern>/`), and on any post that asks for it. The player's code lives in `site/`, but its **reference code lives here**, in `post-kit/viz/<pattern>/ref.py`, in the same shape as a post's `ref.py`. The website's build refuses to finish unless its TypeScript agrees with this Python on every test input.

```
post-kit/viz/
  two-pointers/ref.py      sorted array, find the pair (post 06)
  sliding-window/ref.py    longest run within a budget (post 08)
  monotonic-stack/ref.py   next greater number (no post yet)
site/visualizer/
  schema.ts                the step format (version 1), shared by the site and this kit
  patterns/<pattern>.ts    the same algorithm in TypeScript, one file per pattern
  registry.ts              the list of patterns the build checks
  loaders.ts               how the browser fetches each pattern, one small file each
  access.ts                free and paid patterns (the paywall switch, off for now)
  fixtures/<pattern>.json  test inputs and answers, written by tools/viz_fixtures.py
```

This part runs in plain **Windows PowerShell** too: it only needs Python and Node, not WSL.

### 1. Check that everything agrees

From `site/`:

```
npm run check-viz
```

It prints one `ok` line per pattern and ends with `3 pattern(s), 3947 test inputs, all steps valid`. `npm run build` runs this check every time, right after `check-posts`. For each pattern it checks:

- **Answers:** the TypeScript answer matches the Python brute force on every test input (1,300+ per pattern).
- **Every step:** pointers stay inside the array, the window's total is its real sum, the stack really is in order, and the narration only mentions numbers that are true at that step.
- **The example:** the step-by-step trace of the post's example is exactly what `viz_steps()` produces here.
- **Pseudocode:** it is the same as the `## Pseudocode` block of the pattern's post.

While working, `npm run check-viz -- --sample 50` checks 50 inputs per pattern and takes a second.

### 2. After changing a `ref.py` here

The website doesn't run Python when it builds, so the Python results are saved as files. Write them again whenever a `ref.py` changes, from `site/`:

```
npm run viz-fixtures
```

On WSL, Linux or macOS, where the command is `python3`, run it from the repo root instead:

```
python3 post-kit/tools/viz_fixtures.py
```

It stops if `solve()` and `brute()` disagree on any input, or if there are fewer than 1,000 inputs. Commit the changed `site/visualizer/fixtures/*.json` together with the `ref.py`.

### 3. Show the player on a post

Add one line to the post's frontmatter (the block between the `---` lines at the top of `site/content/posts/NN-slug.mdx`):

```yaml
visualizer: two-pointers
```

The player appears after the post's body, under "Try it on your own input". The value must be one of the pattern names above, or the build stops and names the file. For a post made with this kit, put `"visualizer": "two-pointers"` in the `blog` block of its `post.json` and the kit writes the line into the exported MDX. Posts made before the kit (00 to 21) get the line by hand.

A post with a player must use the same pseudocode as the pattern. If you change one, change the other (`PSEUDOCODE` in `ref.py` and `pseudocode` in `site/visualizer/patterns/<pattern>.ts`), then run step 2.

### 4. Add a new pattern

1. **Reference.** Create `post-kit/viz/<pattern>/ref.py` (copy `sliding-window/ref.py`). It needs:

   | Name | What it is |
   | --- | --- |
   | `PATTERN` | The pattern's name; must equal the folder name |
   | `EXAMPLE` | The post's tiny example, as the default input |
   | `PSEUDOCODE` | The post's pseudocode, one string per line |
   | `solve(inp)` | The real algorithm |
   | `brute(inp)` | The slow, obviously correct answer |
   | `viz_steps(inp)` | The list of steps (format below) |
   | `test_inputs()` | At least 1,000 inputs: edge cases plus random ones |
   | `same(inp, got, want)` | Optional: only when more than one answer is correct |

2. **TypeScript.** Create `site/visualizer/patterns/<pattern>.ts` (copy `sliding-window.ts`). `run()` is the same algorithm, giving the same steps with the same words. `check()` holds the pattern's rules for one step and is written on its own, not by calling `run()`, so a mistake in one is caught by the other.
3. **List it, twice.** Add the pattern to `site/visualizer/registry.ts` (the list the build checks) and to `site/visualizer/loaders.ts` (how the browser fetches it, one small file per pattern). In the pattern's own file set `section` (its roadmap section, which groups the gallery) and `tier`: `"free"` or `"paid"`. Paid changes nothing until `PAYWALL_ON` in `site/visualizer/access.ts` is switched on.
4. **Test.** From `site/`: `npm run viz-fixtures`, then `npm run build`. A mismatch names the input, the step and the two versions.
5. **Look.** `npm run dev` and open `/visualize/<pattern>/`: try your own input, bad input, both themes and a phone-sized window. On a laptop the whole player should fit on one screen.

No change to the player is needed unless the pattern needs a new kind of picture (a grid, a tree). Arrays, pointers, one window, one stack and named values are already drawn.

### The step format (version 1)

Each step is a complete picture, not a change from the step before, so the player can jump to any step. `viz_steps()` returns a list of these:

```python
{
    "line": 5,                                  # index into PSEUDOCODE, counted from 0
    "say": "3 joins the window: total is 6.",   # one plain sentence, at most 110 characters
    "cells": [{"v": 2, "state": "steel"}, ...], # the array; same states as the slides
    "pointers": [{"id": "left", "label": "left", "at": 0}],
    "window": {"lo": 0, "hi": 2},               # optional; lo == hi + 1 means empty
    "stack": [{"id": "s0", "v": 2, "from": 0}], # optional; bottom first
    "vars": [{"name": "total", "value": 6}],    # optional; "" means not set yet
}
```

Cell states are the slides' own: `gold` (the current focus), `steel` (done or compared), `dim` (out of play), `ghost` (a gap), `dash` (an empty slot, value `""`), and `plain`. Keep each `id` the same from step to step: that is how the player knows to slide a pointer or pop a stack item instead of redrawing it.

### What is still separate, and what is planned

- **The video and the website do not share code yet.** The slide video (`kit/video.py`) still uses its own step words from the **Video** section above, and a post's story is written twice: `video_steps()` in `posts/NN-slug/ref.py` for the video, `viz_steps()` in `viz/<pattern>/ref.py` for the website. Drawing the video from this format is planned, after the format's version 2.
- **Version 2 of the format** will make a step a list of typed pictures (array, tree, grid, linked list, call stack, heap, graph), so patterns that are not arrays can be shown. Nothing in this section changes until then.
- **Free and paid.** Each pattern's file says `tier: "free"` or `"paid"`. It has no effect while `PAYWALL_ON` in `site/visualizer/access.ts` is `false`. Switching it on only hides the reader's own input on paid patterns; keeping paid patterns truly private needs a server check, which is not built.
