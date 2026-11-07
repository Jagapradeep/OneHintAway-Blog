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
