#!/usr/bin/env python3
"""One Hint Away post kit.

  python3 post-kit/render.py post-kit/posts/22-insertion-sort            # validate + canvas files + summary
  python3 post-kit/render.py post-kit/posts/22-insertion-sort --png review --video draft
  python3 post-kit/render.py post-kit/posts/22-insertion-sort --png final --video final   # after approval

Writes to build/NN-slug/: project/ (canvas files to publish), summary.txt (the plain-text review),
png/slide-NN.png, slide-02.mp4 (or the video's slot), and prints only errors, warnings and file paths."""
import base64
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

if Path("/opt/pw-browsers").exists():  # the build machine's browser; elsewhere Playwright's default is used
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
FONTS = [("Sora", w, f"sora-latin-{w}-normal.woff2") for w in (600, 700, 800)] + \
        [("Manrope", w, f"manrope-latin-{w}-normal.woff2") for w in (500, 600, 700)] + \
        [("Geist Mono", w, f"geist-mono-latin-{w}-normal.woff2") for w in (500, 600)]
# Fonts are embedded as data URIs: pages loaded with set_content run as about:blank,
# and Chromium refuses file:// fonts from there, which silently fell back to a system font.
FONT_CSS = "".join(
    f"@font-face{{font-family:'{f}';font-weight:{w};font-display:block;"
    f"src:url(data:font/woff2;base64,{base64.b64encode((KIT / 'fonts' / fn).read_bytes()).decode()}) format('woff2');}}"
    for f, w, fn in FONTS)
GFONTS = "https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&amp;family=Manrope:wght@500;600;700&amp;family=Geist+Mono:wght@500;600&amp;display=swap"

CHECK_JS = """() => {
 const root = document.body.firstElementChild, out = [];
 const foot = root.querySelector('[data-chrome="footer"]'), space = root.querySelector('[data-chrome="footer-space"]');
 const head = root.querySelector('[data-chrome="progress"]');
 if (!foot || !space || !head) out.push('slide is missing the fixed header or footer');
 const fr = foot ? foot.getBoundingClientRect() : null;
 if (fr && (Math.abs(fr.bottom - 1286) > 1 || Math.abs(fr.left - 80) > 1 || Math.abs(fr.right - 1000) > 1)) out.push('footer is not in its fixed place');
 if (fr && space && space.getBoundingClientRect().top - fr.top > 6) out.push('content pushes past the footer by ' + Math.round(space.getBoundingClientRect().top - fr.top) + 'px');
 const limit = fr ? fr.top - 22 : 1250, top = head ? head.getBoundingClientRect().bottom : 0;
 for (const e of root.querySelectorAll('*')) {
   if (e.closest('[data-chrome]') || /560px/.test(e.style.fontSize)) continue;
   const cs = getComputedStyle(e), r = e.getBoundingClientRect();
   if (!r.width || !r.height || cs.visibility === 'hidden') continue;
   if (r.bottom > limit + 6) out.push('runs into the footer (' + Math.round(r.bottom - limit) + 'px): ' + e.textContent.trim().slice(0, 40));
   if (r.top < top - 1) out.push('runs into the header: ' + e.textContent.trim().slice(0, 40));
   if (cs.whiteSpace === 'nowrap' && e.scrollWidth > e.clientWidth + 1 && e.clientWidth > 0) out.push('text cut off: ' + e.textContent.slice(0, 40));
   if ((r.right > 1001 || r.left < 79) && e.textContent.trim()) out.push('leaves the margins: ' + e.textContent.trim().slice(0, 40));
 }
 return [...new Set(out)].slice(0, 6);
}"""


def dc_file(title, slide_html):
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<title>" + title + "</title>\n"
            "<script src=\"./support.js\"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n<link href=\"" + GFONTS + "\" rel=\"stylesheet\">\n"
            "<style>\nbody{margin:0}\n</style>\n</helmet>\n" + slide_html + "\n</x-dc>\n"
            "<script type=\"text/x-dc\" data-dc-script data-props='{\"$preview\":{\"width\":1080,\"height\":1350}}'>\n"
            "class Component extends DCLogic {\nrenderVals() {\nreturn {};\n}\n}\n</script>\n</body>\n</html>\n")


def plain_page(slide_html):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{FONT_CSS}body{{margin:0}}</style></head><body>{slide_html}</body></html>"


def posting_dates(start, n, daily=False):
    """One posting date per post: the next weekdays, or every calendar day with daily=True."""
    import datetime as dt
    d, out = dt.date.fromisoformat(start), []
    while len(out) < n:
        if daily or d.weekday() < 5:
            out.append(d.isoformat())
        d += dt.timedelta(days=1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folders", nargs="+", help="one or more posts/NN-slug folders")
    ap.add_argument("--out", help="output folder (default ./build)")
    ap.add_argument("--png", choices=["review", "final"])
    ap.add_argument("--video", choices=["draft", "final"])
    ap.add_argument("--test", action="store_true", help="run the four-language tests against ref.py")
    ap.add_argument("--export", action="store_true", help="final PNGs + MP4 + MDX + caption + alt text, zipped per post")
    ap.add_argument("--start", help="posting date of the first post (YYYY-MM-DD); later posts take the next weekdays")
    ap.add_argument("--daily", action="store_true", help="with --start: later posts take the next calendar days, weekends included")
    ap.add_argument("--force", action="store_true", help="render even if validation fails")
    a = ap.parse_args()
    if a.export:
        a.png, a.video, a.test = "final", "final", True
    folders = sorted(Path(f) for f in a.folders)
    import datetime as dt
    dates = posting_dates(a.start or dt.date.today().isoformat(), len(folders), a.daily)
    failed = [f.name for f, d in zip(folders, dates) if not one(f, a, d)]
    if len(folders) > 1:
        print(f"\nDONE {len(folders) - len(failed)}/{len(folders)} posts" + (f"; FAILED: {', '.join(failed)}" if failed else ""))
    sys.exit(1 if failed else 0)


def one(folder, a, published):
    from kit import blog as B
    post, ns = P.load(folder)
    errors = []
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
    out_root = Path(a.out or Path.cwd() / "build")
    out = out_root / folder.name
    tested = 0
    if a.test:
        tested, terr = B.run_tests(folder, ns, out / "test")
        errors += [f"tests: {e}" for e in terr]
        if not terr:
            print(f"{folder.name}: tests passed in Java, Python, C++ and JavaScript on {tested:,} inputs")
    if a.export:
        if "caption" not in post or "blog" not in post or not (folder / "blog.md").exists():
            errors.append("export needs 'caption' and 'blog' in post.json and a blog.md")
    print(f"== {folder.name}" if len(a.folders) > 1 else "", end="\n" if len(a.folders) > 1 else "")
    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print("  -", e)
        if not a.force:
            return False
    for w in warns:
        print("WARNING:", w)
    (out / "project").mkdir(parents=True, exist_ok=True)
    slides = P.build(post, ns, seq, V.stage_div(vslide["video"]) if vslide else None)
    bad_layout = False
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch(args=["--disable-lcd-text", "--font-render-hinting=none"])
        page = br.new_page(viewport={"width": 1080, "height": 1350})
        vs = next((x for x in slides if x["type"] == "video"), None)
        if vs:
            page.set_content(V.player_page(vs["html"], tl, FONT_CSS))
            page.evaluate("document.fonts.ready")
            n_st = len(tl["states"])
            for k in range(n_st):
                st = tl["states"][k]
                times = [st["t0"] + st["len"] - 0.05] if k < n_st - 1 else [tl["duration"] - V.FADE - 0.05]
                times.insert(0, st["t0"] + st["mv"] * 0.5)
                seen = []
                for j, t in enumerate(times):
                    page.evaluate(f"window.draw({t})")
                    seen += [i for i in page.evaluate(f"window.check({'true' if j else 'false'})") if i not in seen]
                for issue in seen:
                    bad_layout = True
                    print(f"LAYOUT slide {vs['n']:02d} (video, step {k + 1} of {n_st}):", issue)
            page.evaluate(f"window.draw({tl['duration'] - V.FADE - 0.01})")
            still = page.evaluate("document.getElementById('stage').outerHTML").replace(' id="stage"', "")
            vs["player_html"] = vs["html"]
            vs["html"] = vs["html"].replace(V.stage_div(vslide["video"]), still)
        for x in slides:
            if P.ui.FIT_OPEN in x["html"]:      # fill the slide: draw a sparse slide's content larger
                page.set_content(plain_page(x["html"]))
                page.evaluate("document.fonts.ready")
                z, gap = page.evaluate(P.ui.FIT_JS, [list(P.ui.FIT_STEPS), P.ui.FIT_MIN_ROOM, P.ui.FIT_KEEP])
                if z != 1 or gap:
                    x["html"] = x["html"].replace(P.ui.FIT_OPEN, P.ui.fitted(z, gap))
            page.set_content(plain_page(x["html"]))
            page.evaluate("document.fonts.ready")
            r = page.evaluate(CHECK_JS)
            if r:
                bad_layout = True
                print(f"LAYOUT slide {x['n']:02d}:", "; ".join(r))
        if bad_layout and not a.force:
            print("LAYOUT FAILED: fix the slides above first (or pass --force for a look)")
            br.close()
            return False
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
    if a.export:
        return export(folder, post, ns, seq, slides, vs, out, tested, published)
    print(f"OK {len(slides)} slides, video {vdur:.1f}s -> {out}")
    return True


def export(folder, post, ns, seq, slides, vs, out, tested, published):
    from kit import blog as B
    import shutil
    name = f"{post['number']:02d}-{post['slug']}"
    pk = out / name
    if pk.exists():
        shutil.rmtree(pk)
    pk.mkdir()
    for x in slides:
        src = out / (f"slide-{x['n']:02d}.mp4" if vs and x is vs else f"png/slide-{x['n']:02d}.png")
        shutil.copyfile(src, pk / src.name)
    # blog page: protect the kit's markers, compute {{ }} from ref.py, then fill the markers
    body = (folder / "blog.md").read_text()
    marks = {k: f"@@{k}@@" for k in ("PSEUDOCODE", "CODE", "TESTED")}
    for k, m in marks.items():
        body = body.replace("{{" + k + "}}", m)
    errs = []
    body = P._subst(body, ns, errs)
    for k, m in marks.items():
        body = body.replace(m, "{{" + k + "}}")
    mdx = B.mdx(post, ns, seq, folder, tested, published, len(slides), vs["n"] if vs else None, body)
    (pk / f"{name}.mdx").write_text(mdx)
    cap, cerr = B.caption(post)
    (pk / "caption.txt").write_text(cap)
    (pk / "alt-text.txt").write_text(B.alt_texts(post, seq))
    errs += cerr
    (out / "pseudo.txt").write_text(B.pseudocode(seq) + "\n")
    if not (KIT / "tools" / "node_modules" / "@mdx-js").exists():
        subprocess.run("npm i --silent --no-save gray-matter@4 @mdx-js/mdx@3 remark-gfm@4 remark-frontmatter@5",
                       shell=True, cwd=KIT / "tools", capture_output=True)
    chk = subprocess.run(["node", str(KIT / "tools" / "check_mdx.mjs"), str(pk / f"{name}.mdx"), "--slides", str(pk),
                          "--pseudo", str(out / "pseudo.txt")], capture_output=True, text=True)
    report = (chk.stdout + chk.stderr).strip()
    if chk.returncode:
        errs.append("MDX check failed:\n" + report[-1500:])
    elif "WARN" in report.upper():
        print(report[-800:])
    for f in pk.iterdir():
        if f.stat().st_size > 25 * 1024 * 1024:
            errs.append(f"{f.name} is over 25 MB")
    if errs:
        print("EXPORT FAILED:")
        for e in errs:
            print("  -", e)
        return False
    z = shutil.make_archive(str(out.parent / name), "zip", out, name)
    print(f"OK {name}: {len(slides)} slides, posting {published}, {Path(z).stat().st_size / 1e6:.1f} MB -> {z}")
    return True


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
                r = subprocess.run([sys.executable, str(deband), str(big), str(f)], capture_output=True, text=True)
                if r.returncode:
                    sys.exit(f"deband.py failed on {big.name}:\n{r.stderr.strip()}\n"
                             "(missing packages? pip install --break-system-packages opencv-python-headless numpy scipy pillow)")
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
