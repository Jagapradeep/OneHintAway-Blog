# One Hint Away post kit

Turns one small content file into a finished carousel: canvas slides, the motion video, PNGs and a plain-text review summary. Claude writes **content only**; every layout, colour, footer, counter and number comes from here.

```
post-kit/
  render.py            the one command
  kit/ui.py            Graphite & Chrome v3.1 pieces (copied from posts 22 and 18)
  kit/post.py          templates, derived values, validator, summary
  kit/video.py         generic motion slide (timeline + player + MP4)
  fonts/               Sora, Manrope, Geist Mono (SIL OFL), so renders never fall back
  tools/deband.py      final-export banding fix
  posts/NN-slug/       post.json (content) + ref.py (reference code: every number comes from it)
  used_problems.json   practice problems already used, by post number
```

## Run it

```
python3 post-kit/render.py post-kit/posts/22-insertion-sort                      # check + canvas files + summary.txt
python3 post-kit/render.py post-kit/posts/22-insertion-sort --png review --video draft
python3 post-kit/render.py post-kit/posts/22-insertion-sort --png final --video final   # after approval
```

Output goes to `build/NN-slug/`: `project/` (publish to the Design canvas), `summary.txt`, `png/`, `slide-NN.mp4`.

## Templates

- **concept** (7 slides): cover, video, story, picture + quick check, template, trap + cost, practice. Up to 2 `extra` slides may sit between picture and template (two-topic posts like power and modulo).
- **challenge** (13 slides): cover, story, problem, pause, 4 hints (3–5 allowed), bridge, video, 2 solution slides (1–2 allowed), closing.

## What is derived (cannot be typed wrong)

Slide counter, progress bar, footer teasers (each slide's `teaser` shows on the slide before it), "BY SLIDE N", "in N lines", read time, answer banner after a quick check, hint and solution labels, solution line numbers, the bridge's "next N slides", the closing AI prompt, the blog line, every `{{expression}}` (computed by `ref.py`), and every number in the video.

## What the validator refuses

Wrong slide order or count for the template; a story without a `scene`; a quick check whose answer doesn't match `ref.py`; a cost that isn't Big-O; an example whose output doesn't match; a practice hint too slow for the problem's limits (complexity at max input > 10⁸, unless marked `partial`); banned hook words; teasers over 34 characters. Layout check after rendering: content past 1,250 px, text cut off, anything leaving the slide.

## Video

Steps describe states (`swap`, `move`, `set`, `gold`, `steel`, `frame`, `band`, `ptr`, `water`, `eq`, `chip`, `caption`); `ref.py` usually generates them by running the real algorithm. Two stages: `boxes` (arrays) and `bars` (heights and water). Pacing is design.md 6b. Frames that don't change are reused, not re-rendered (about 40% of a typical video).
