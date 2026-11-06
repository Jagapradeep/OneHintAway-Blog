#!/usr/bin/env python3
"""One Hint Away post kit.

  python3 post-kit/render.py post-kit/posts/22-insertion-sort            # validate + canvas files + summary
  python3 post-kit/render.py post-kit/posts/22-insertion-sort --png review --video draft
  python3 post-kit/render.py post-kit/posts/22-insertion-sort --png final --video final   # after approval

Writes to build/NN-slug/: project/ (canvas files to publish), summary.txt (the plain-text review),
png/slide-NN.png, slide-02.mp4 (or the video's slot), and prints only errors, warnings and file paths."""
import argparse
import json
import math
import os
import subprocess
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))
from kit import post as P, video as V  # noqa: E402

os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
FONTS = [("Sora", w, f"sora-latin-{w}-normal.woff2") for w in (600, 700, 800)] + \
        [("Manrope", w, f"manrope-latin-{w}-normal.woff2") for w in (500, 600, 700)] + \
        [("Geist Mono", w, f"geist-mono-latin-{w}-normal.woff2") for w in (500, 600)]
FONT_CSS = "".join(f"@font-face{{font-family:'{f}';font-weight:{w};src:url('file://{KIT}/fonts/{fn}') format('woff2');}}" for f, w, fn in FONTS)
GFONTS = "https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&amp;family=Manrope:wght@500;600;700&amp;family=Geist+Mono:wght@500;600&amp;display=swap"

CHECK_JS = """() => {
 const root = document.body.firstElementChild, out = [];
 const spacer = [...root.children].reverse().find(c => c.style.marginTop === 'auto');
 const end = spacer ? spacer.getBoundingClientRect().top : 0;
 if (end > 1252) out.push('content ends at ' + Math.round(end) + 'px (keep it above 1250)');
 if (spacer && spacer.getBoundingClientRect().height < 0) out.push('slide overflows');
 for (const e of root.querySelectorAll('*')) {
   const cs = getComputedStyle(e);
   if (cs.whiteSpace === 'nowrap' && e.scrollWidth > e.clientWidth + 1 && e.clientWidth > 0) out.push('text cut off: ' + e.textContent.slice(0, 40));
   const r = e.getBoundingClientRect();
   if (r.width && (r.right > 1081 || r.left < -1) && !/560px/.test(e.style.fontSize)) out.push('leaves the slide: ' + e.textContent.slice(0, 40));
 }
 return [...new Set(out)];
}"""


def dc_file(title, slide_html):
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<title>" + title + "</title>\n"
            "<script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n<link href=\"" + GFONTS + "\" rel=\"stylesheet\">\n"
            "<style>\nbody{margin:0}\n</style>\n</helmet>\n" + slide_html + "\n</x-dc>\n"
            "<script type=\"text/x-dc\" data-dc-script data-props='{\"$preview\":{\"width\":1080,\"height\":1350}}'>\n"
            "class Component extends DCLogic {\nrenderVals() {\nreturn {};\n}\n}\n</script>\n</body>\n</html>\n")


def plain_page(slide_html):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{FONT_CSS}body{{margin:0}}</style></head><body>{slide_html}</body></html>"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--out")
    ap.add_argument("--png", choices=["review", "final"])
    ap.add_argument("--video", choices=["draft", "final"])
    ap.add_argument("--force", action="store_true", help="render even if validation fails")
    a = ap.parse_args()
    folder = Path(a.folder)
    post, ns = P.load(folder)
    errors = []
    # video steps may come from ref.py
    for s in post["slides"]:
        if s["type"] == "video" and isinstance(s["video"].get("steps"), str):
            s["video"]["steps"] = eval(s["video"]["steps"], dict(ns))
    post = P._subst(post, ns, errors)
    seq, e2 = P.expand(post)
    errors += e2
    e3, warns = P.validate(post, ns, seq)
    errors += e3
    vslide = next((s for t, s in seq if t == "video"), None)
    tl = V.timeline(vslide["video"]) if vslide else None
    vdur = tl["duration"] if tl else 0
    post["_read_time"] = f"About {max(1, math.ceil(((len(seq) - (1 if vslide else 0)) * 10 + vdur) / 60))} min"
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print("  -", e)
        if not a.force:
            sys.exit(1)
    for w in warns:
        print("WARNING:", w)

    out = Path(a.out or Path.cwd() / "build" / folder.name)
    (out / "project").mkdir(parents=True, exist_ok=True)
    slides = P.build(post, ns, seq, V.stage_div(vslide["video"]) if vslide else None)

    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=["--disable-lcd-text", "--font-render-hinting=none"])
        page = br.new_page(viewport={"width": 1080, "height": 1350})
        vs = next((x for x in slides if x["type"] == "video"), None)
        if vs:
            page.set_content(V.player_page(vs["html"], tl, FONT_CSS))
            page.evaluate("document.fonts.ready")
            page.evaluate(f"window.draw({tl['duration'] - V.FADE - 0.01})")
            still = page.evaluate("document.getElementById('stage').outerHTML").replace(' id="stage"', "")
            vs["player_html"] = vs["html"]
            vs["html"] = vs["html"].replace(V.stage_div(vslide["video"]), still)
        problems = {}
        for x in slides:
            page.set_content(plain_page(x["html"]))
            page.evaluate("document.fonts.ready")
            r = page.evaluate(CHECK_JS)
            if r:
                problems[x["n"]] = r
        for n, r in problems.items():
            print(f"LAYOUT slide {n:02d}:", "; ".join(r))
        if a.png:
            render_pngs(br, slides, out, 1 if a.png == "review" else 3)
        if a.video and vs:
            render_video(br, vs, tl, out, a.video)
        br.close()

    boards, order = {}, []
    for i, x in enumerate(slides):
        (out / "project" / x["name"]).write_text(dc_file(x["board"], x["html"]))
        boards[x["name"]] = {"x": i * 1160, "y": 0, "w": 1080, "h": 1350, "title": x["board"]}
        order.append(x["name"])
    title = f"One Hint Away · {post['number']:02d} · {post['topic']}"
    canvas = {"v": 3, "createdOnFiles": {"v": 1, "at": "2026-01-01T00:00:00Z"}, "title": title, "launch": {"view": "canvas"},
              "pages": [], "boards": boards, "order": order, "designSystems": [],
              "notes": {"heading": {"x": 0, "y": -300, "text": title, "kind": "title1", "maxW": len(slides) * 1160 - 80}}}
    (out / "project" / "canvas.json").write_text(json.dumps(canvas, indent=1, ensure_ascii=False))
    (out / "summary.txt").write_text(P.summary(post, seq, vdur, warns))
    print(f"OK {len(slides)} slides, video {vdur:.1f}s -> {out}")


def render_pngs(br, slides, out, scale):
    from PIL import Image
    pg = br.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=scale)
    (out / "png").mkdir(exist_ok=True)
    for x in slides:
        pg.set_content(plain_page(x["html"]))
        pg.evaluate("document.fonts.ready")
        f = out / "png" / f"slide-{x['n']:02d}.png"
        pg.screenshot(path=str(f))
        if scale != 1:
            deband = KIT / "tools" / "deband.py"
            big = f.with_name(f.stem + "@3x.png")
            f.rename(big)
            if deband.exists():
                subprocess.run([sys.executable, str(deband), str(big), str(f)], check=True, capture_output=True)
            else:
                Image.open(big).convert("RGB").resize((1080, 1350), Image.LANCZOS).save(f)
            big.unlink()
    pg.close()


def render_video(br, vs, tl, out, quality):
    fps, scale = (30, 1) if quality == "draft" else (60, 2)
    pg = br.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=scale)
    pg.set_content(V.player_page(vs["player_html"], tl, FONT_CSS))
    pg.evaluate("document.fonts.ready")
    cdp = pg.context.new_cdp_session(pg)
    import base64
    mp4 = out / f"slide-{vs['n']:02d}.mp4"
    enc = (["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p"] if quality == "draft" else
           ["-vf", "scale=1080:1350:flags=lanczos,format=yuv420p", "-c:v", "libx264", "-profile:v", "high", "-level", "4.2",
            "-preset", "slow", "-crf", "12", "-tune", "animation", "-x264-params", f"keyint={fps}:min-keyint={fps}",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709"])
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "png", "-i", "-",
                           *enc, "-movflags", "+faststart", "-an", str(mp4)], stdin=subprocess.PIPE)
    nframes = int(round(tl["duration"] * fps))
    last_sig, last_png, unique = None, None, 0
    for i in range(nframes):
        sig = pg.evaluate(f"window.draw({i / fps})")
        if sig != last_sig:
            last_png = base64.b64decode(cdp.send("Page.captureScreenshot", {"format": "png", "optimizeForSpeed": True})["data"])
            last_sig = sig
            unique += 1
        ff.stdin.write(last_png)
    ff.stdin.close()
    ff.wait()
    pg.close()
    print(f"video: {nframes} frames ({unique} rendered, {nframes - unique} reused) -> {mp4}")


if __name__ == "__main__":
    main()
