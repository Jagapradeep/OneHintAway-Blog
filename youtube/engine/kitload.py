"""Load a post through the real post kit: substituted post, the video slide, its timeline, fonts, ui."""
import sys, json, base64
from pathlib import Path
KIT = Path(__file__).resolve().parents[2] / "post-kit"   # the repo's post kit
sys.path.insert(0, str(KIT))
from kit import post as P, video as V, ui as U  # noqa

FONTS = [("Sora", w, f"sora-latin-{w}-normal.woff2") for w in (600, 700, 800)] + \
        [("Manrope", w, f"manrope-latin-{w}-normal.woff2") for w in (500, 600, 700)] + \
        [("Geist Mono", w, f"geist-mono-latin-{w}-normal.woff2") for w in (500, 600)]
FONT_CSS = "".join(
    f"@font-face{{font-family:'{f}';font-weight:{w};font-display:block;"
    f"src:url(data:font/woff2;base64,{base64.b64encode((KIT / 'fonts' / fn).read_bytes()).decode()}) format('woff2');}}"
    for f, w, fn in FONTS)

def load(slug):
    folder = KIT / "posts" / slug
    post, ns = P.load(folder)
    for s in post["slides"]:
        if s["type"] == "video" and isinstance(s["video"].get("steps"), str):
            s["video"]["steps"] = eval(s["video"]["steps"], dict(ns))
    errors = []
    post = P._subst(post, ns, errors)
    assert not errors, errors
    v = next(s for s in post["slides"] if s["type"] == "video")["video"]
    tl = V.timeline(v)
    return post, ns, v, tl

def kit_player_js():
    # rename the kit's global so our own draw(t) can drive it with local time
    return V.PLAYER_JS.replace("window.draw", "window.kitDraw").replace("window.check", "window.kitCheck")

def stage_div(v, extra_style=""):
    L = V.layout(v)
    return f'<div id="stage" style="position: relative; width: 920px; height: {L["height"]}px;{extra_style}"></div>', L["height"]

if __name__ == "__main__":
    for slug in sys.argv[1:]:
        post, ns, v, tl = load(slug)
        print("==", slug, "dur", tl["duration"], "stage h", tl["layout"].get("height"))
        for i, s in enumerate(tl["states"]):
            print(f"  {i:2} t0={s['t0']:5} len={s['len']:4} mv={s['mv']} cap={s['caption']!r} eq={s['eq']}")
