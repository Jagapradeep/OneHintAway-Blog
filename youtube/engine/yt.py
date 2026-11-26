"""One Hint Away video maker: one script.json per video set -> long video + Shorts, voiced, captioned.

    youtube/scripts/NN-slug/script.json   long, short (or shorts: [...]), youtube text; optional ref.py
    python3 youtube/engine/yt.py youtube/scripts/NN-* [--video long|short|both|all] [--draft] [--out DIR]

Checks the script, builds the timeline with the real voice, renders one still per scene (its end state)
in every format, and fails on any layout overflow or broken rule. --video renders MP4s and .srt captions.
Pattern posts reuse their post kit folder: "post": "28-binary-search" gives {{...}} access to its ref.py,
"lines_from" pulls code from its slides, and the "kit" layout plays its motion video in sync with the voice.
"""
import argparse, importlib.util, json, re, sys
from pathlib import Path
from html import escape
import engine as E
import kitload as K
from kitload import U

GOLD, STEEL, RED, MUTED = "#F4CF6E", "#A3CDF2", "#E5736B", "#A2A8B3"
FMT = {
    "long": dict(W=1920, H=1080, sc=(150, 110, 1620, 810), title=84, body=46, mono=38, cell=170, caps_top=948, cap_chars=60,
                 caps="left:210px;width:1500px;top:948px;font-size:44px;line-height:56px", top_safe=96, logo="right:80px;top:44px"),
    "short": dict(W=1080, H=1920, sc=(80, 200, 920, 1110), title=88, body=48, mono=34, cell=150, caps_top=1340, cap_chars=28,
                  caps="left:100px;width:880px;top:1340px;font-size:54px;line-height:68px;text-wrap:balance", top_safe=200, logo="left:80px;top:74px"),
}
LIMITS = {"long": (90, 480), "short": (20, 58)}
HYPE = re.compile(r"\b(easy|easily|simple|simply|just|everyone|everybody|most people|almost every|every beginner|always works|guarantee\w*|crack|faang|secret|insane|never forget)\b", re.I)
SPOKEN_BAD = re.compile(r"[()\[\]²³=→<>_`{}]|\.com|\bO\(|\bn\^")
KEYS = {"id", "layout", "label", "title", "say", "chapter", "kicker", "sub", "items", "head", "rows", "lines", "values", "under",
        "states", "wrong", "right", "text", "next", "practice", "cols", "mono", "note", "post", "widths", "site", "at", "checks", "compact", "lines_from", "steps", "from_post", "slow"}
LAYOUTS = {"kit", "outro", "title", "big", "list", "table", "code", "boxes", "compare", "pause", "end"}


# ------------------------------------------------------------------ loading
def channel(folder):
    f = Path(folder).resolve().parent.parent / "channel.json"
    return json.loads(f.read_text()) if f.exists() else {}

def load(folder):
    folder = Path(folder)
    spec = json.loads((folder / "script.json").read_text())
    spec["_channel"] = channel(folder)
    ns = {}
    if spec.get("post"):
        ns.update(K.load(spec["post"])[1])
    ref = folder / "ref.py"
    if ref.exists():
        m = importlib.util.spec_from_file_location("ref_" + folder.name.replace("-", "_"), ref)
        mod = importlib.util.module_from_spec(m); m.loader.exec_module(mod)
        ns = {k: getattr(mod, k) for k in dir(mod) if not k.startswith("__")}
    errors = []

    def sub(x):
        if isinstance(x, str):
            def rep(mt):
                expr, fspec = mt.group(1), None
                m2 = re.match(r"^(.+?):([,.0-9a-z%]+)$", expr)
                if m2:
                    expr, fspec = m2.groups()
                try:
                    v = eval(expr, dict(ns))
                    if fspec:
                        return format(v, fspec)
                except Exception as e:  # noqa
                    errors.append(f"{{{{{mt.group(1)}}}}}: {e}"); return "?"
                return f"{v:,}" if isinstance(v, int) and abs(v) >= 10000 else str(v)
            return re.sub(r"\{\{(.+?)\}\}", rep, x)
        if isinstance(x, list):
            return [sub(i) for i in x]
        if isinstance(x, dict):
            return {k: sub(v) for k, v in x.items()}
        return x
    spec = sub(spec)
    for fmt in formats(spec):
        for sc in spec[fmt]["scenes"]:
            lf = sc.get("lines_from")
            if lf:
                try:
                    post = K.load(lf.get("post", spec.get("post")))[0]
                    slides = [x for x in post["slides"] if x["type"] == lf["slide"]]
                    lines = list(slides[lf.get("n", 0)]["code"]["lines"])
                    for k, txt in lf.get("edit", {}).items():   # {"4": "    while low < high:"}: show the trap's wrong line
                        lines[int(k) - 1] = txt
                    sc["lines"] = lines
                except Exception as e:  # noqa
                    errors.append(f"{fmt}/{sc['id']}: lines_from {lf}: {e}")
    for chk in spec.get("checks", []):          # [expression, expected]: facts the script states, proven by ref.py
        try:
            got = eval(chk[0], dict(ns))
            if got != chk[1]:
                errors.append(f"check {chk[0]} = {got!r}, script says {chk[1]!r}")
        except Exception as e:  # noqa
            errors.append(f"check {chk[0]}: {e}")
    return spec, errors


# ------------------------------------------------------------------ text helpers
def rich(s):
    s = escape(str(s), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r'<b class="g">\1</b>', s, flags=re.S)
    s = re.sub(r"`(.+?)`", r'<code>\1</code>', s, flags=re.S)
    return s.replace("\n", "<br>")

def at(i, until=None, fx="rise"):
    a = f' data-at="L{i}"' if isinstance(i, int) else f' data-at="{i}"'
    if until is not None:
        a += f' data-until="L{until}"' if isinstance(until, int) else f' data-until="{until}"'
    return a + f' data-fx="{fx}"'

def lines_of(sc):
    src = [sc["steps"][k] for k in sorted(sc["steps"], key=int)] if "steps" in sc else sc.get("say", [])
    return [l if isinstance(l, dict) else {"say": l} for l in src]

def formats(spec):
    """'long', 'short' and, for several Shorts, 'short2', 'short3'... (from a 'shorts' list)."""
    if "shorts" in spec and "short" not in spec:
        for i, sh in enumerate(spec["shorts"]):
            spec["short" if i == 0 else f"short{i + 1}"] = sh
    return [k for k in spec if k == "long" or re.fullmatch(r"short\d*", k)]

def kind(fmt):
    return "long" if fmt == "long" else "short"


# ------------------------------------------------------------------ layouts
def head(sc, F):
    h = ""
    if sc.get("label"):
        h += f'<div class="pill"><span></span>{escape(sc["label"])}</div>'
    if sc.get("title"):
        h += f'<div class="ttl" style="font-size:{F["title"]}px">{U.title_html(sc["title"])}</div>'
    return h

def lay_title(sc, F, fmt):
    k = f'<div class="pill">{escape(sc["kicker"])}</div>' if sc.get("kicker") else ""
    size = 124 if fmt == "long" else 112
    sub = f'<div class="lead" {at(sc.get("sub_at", 1))} style="margin-top:34px;font-size:{F["body"] + 6}px;max-width:1300px">{rich(sc["sub"])}</div>' if sc.get("sub") else ""
    return (f'<div class="center">{k}<div class="ttl" style="font-size:{size}px;line-height:1.02;margin-top:26px">{U.title_html(sc["title"])}</div>{sub}</div>')

def lay_big(sc, F, fmt):
    parts = []
    for it in sc.get("items", []):
        st = it.get("style", "lead")
        cls = {"mono": "bigmono", "lead": "lead", "gold": "biggold"}[st]
        parts.append(f'<div class="{cls}"{at(it.get("at", 0))} style="margin-top:28px">{rich(it["text"])}</div>')
    return head(sc, F) + f'<div class="center" style="flex:none;margin-top:40px">{"".join(parts)}</div>'

def lay_list(sc, F, fmt):
    cols = 1 if fmt == "short" else sc.get("cols", 2)
    cards = []
    for i, it in enumerate(sc["items"]):
        acc = {"gold": GOLD, "red": RED, "steel": STEEL}.get(it.get("accent"), None)
        hd = f'<div class="chead" style="color:{acc or STEEL}">{escape(it["head"])}</div>' if it.get("head") else ""
        cards.append(f'<div class="card{" acc" if acc else ""}"{at(it.get("at", i))} style="{"border-color:" + acc if acc else ""}">'
                     f'{hd}<div class="ctext">{rich(it["text"])}</div></div>')
    return head(sc, F) + f'<div class="grid" style="grid-template-columns:repeat({cols},1fr)">{"".join(cards)}</div>'

def lay_table(sc, F, fmt):
    mono = set(sc.get("mono", []))
    w = sc.get("widths")
    gt = " ".join(w) if w else f"repeat({len(sc['head'])}, auto)"
    cells = "".join(f'<div class="th">{escape(h)}</div>' for h in sc["head"])
    for r, row in enumerate(sc["rows"]):
        a = at(sc.get("at", list(range(len(sc["rows"]))))[r])
        for c, v in enumerate(row):
            cells += f'<div class="td{" m" if c in mono else ""}"{a}>{rich(v)}</div>'
    note = f'<div class="lead"{at(sc["note"]["at"])} style="margin-top:26px">{rich(sc["note"]["text"])}</div>' if sc.get("note") else ""
    return head(sc, F) + f'<div class="tbl{" compact" if sc.get("compact") else ""}" style="grid-template-columns:{gt}">{cells}</div>{note}'

def lay_code(sc, F, fmt, say):
    n = len(sc["lines"]); appear = [0] * n
    ups = [(i, l["upto"]) for i, l in enumerate(say) if "upto" in l]
    for k in range(n):
        appear[k] = next((i for i, u in ups if u > k), 0) if ups else 0
    rows = "".join(f'<div class="cl" data-n="{k + 1}"{at(appear[k], fx="none")}><i>{k + 1}</i><span>{escape(t) or "&nbsp;"}</span></div>'
                   for k, t in enumerate(sc["lines"]))
    note = f'<div class="lead"{at(sc["note"]["at"])} style="margin-top:24px">{rich(sc["note"]["text"])}</div>' if sc.get("note") else ""
    longest = max(len(t) for t in sc["lines"]) + 4
    tall = F["sc"][3] - (250 if sc.get("title") else 150) - (80 if sc.get("note") else 0)
    fs = int(min(F["mono"] * (1.3 if fmt == "short" else 1), (F["sc"][2] - 90) / (0.6 * longest), tall / (n * 1.45 + 1.2)))
    return head(sc, F) + f'<div class="code" style="font-size:{fs}px">{rows}</div>{note}'

def lay_boxes(sc, F, fmt):
    vals = sc["values"]
    n = max(len(st.get("values", vals)) for st in sc["states"])
    cell = int(min(F["cell"], (F["sc"][2] - 18 * (n - 1)) / n))
    layers = []
    states = sc["states"]
    for j, st in enumerate(states):
        nxt = states[j + 1]["at"] if j + 1 < len(states) else None
        bx = ""
        for k, v in enumerate(st.get("values", vals)):
            cls = next((c for c in ("gold", "steel", "dim", "red") if k in st.get(c, [])), "plain")
            v = str(v)
            if v == "→":
                cls = "arrow"
            fs = int(cell * 0.4 * min(1, 2.4 / max(len(v), 1)))
            bx += f'<div class="bx {cls}" style="width:{cell}px;height:{cell}px;font-size:{fs}px">{escape(v)}</div>'
        idx = "".join(f'<div style="width:{cell}px">{escape(str(u))}</div>' for u in sc.get("under", []))
        idx = f'<div class="under">{idx}</div>' if idx else ""
        note = f'<div class="lead" style="margin-top:30px;text-align:center">{rich(st["note"])}</div>' if st.get("note") else ""
        first = j == 0
        layers.append(f'<div{at(st["at"], nxt, fx="rise" if first else "none")}><div class="row">{bx}</div>{idx}{note}</div>')
    return head(sc, F) + f'<div class="stack" style="margin-top:50px">{"".join(layers)}</div>'

def lay_compare(sc, F, fmt):
    out = []
    for key, col, word in (("wrong", RED, "WRONG"), ("right", GOLD, "RIGHT")):
        c = sc[key]
        code = "".join(f'<div>{escape(t)}</div>' for t in c.get("code", []))
        out.append(f'<div class="card"{at(c.get("at", 0 if key == "wrong" else 1))} style="border-color:{col}">'
                   f'<div class="chead" style="color:{col}">{escape(c.get("head", word))}</div>'
                   + (f'<div class="cmono">{code}</div>' if code else "")
                   + (f'<div class="ctext" style="margin-top:14px">{rich(c["text"])}</div>' if c.get("text") else "")
                   + (f'<div class="res" style="color:{col}">{rich(c["result"])}</div>' if c.get("result") else "") + '</div>')
    cols = 1 if fmt == "short" else 2
    note = f'<div class="lead"{at(sc["note"]["at"])} style="margin-top:28px">{rich(sc["note"]["text"])}</div>' if sc.get("note") else ""
    return head(sc, F) + f'<div class="grid" style="grid-template-columns:repeat({cols},1fr)">{"".join(out)}</div>{note}'

def lay_pause(sc, F, fmt):
    return (head(sc, F) + f'<div class="center" style="flex:1">'
            f'<div class="lead" style="font-size:{F["body"] + 8}px;text-align:center">{rich(sc.get("text", ""))}</div>'
            '<div class="cd" data-at="count" data-fx="pop" style="margin-top:50px;display:flex;align-items:center;gap:26px">'
            '<svg width="120" height="120" viewBox="0 0 150 150"><circle cx="75" cy="75" r="64" fill="none" stroke="#2B2F37" stroke-width="10"/>'
            f'<circle class="ring" cx="75" cy="75" r="64" fill="none" stroke="{GOLD}" stroke-width="10" stroke-linecap="round" stroke-dasharray="402" transform="rotate(-90 75 75)"/>'
            '<text class="num" x="75" y="75" text-anchor="middle" dominant-baseline="central" style="font-family:Sora;font-weight:800;font-size:64px;fill:#FFE3A0">2</text></svg>'
            '<div style="font-family:Sora;font-weight:700;font-size:44px;color:#F5F6F8">Pause. Try it.</div></div></div>')

def lay_end(sc, F, fmt):
    pr = ""
    for i, p in enumerate(sc.get("practice", [])):
        pr += (f'<div class="card"{at(p.get("at", 0))}><div class="chead" style="color:{GOLD if p["level"] == "Medium" else STEEL}">'
               f'{escape(p["level"].upper())} · LEETCODE {p["id"]}</div><div class="ctext" style="font-family:Sora;font-weight:700;font-size:{F["body"] + 4}px">{escape(p["title"])}</div>'
               + (f'<div class="ctext" style="margin-top:8px;color:{MUTED}">{rich(p["note"])}</div>' if p.get("note") else "") + '</div>')
    nx = sc.get("next")
    nxt = (f'<div class="card acc"{at(nx.get("at", 1))} style="border-color:{GOLD}"><div class="chead" style="color:{GOLD}">NEXT VIDEO</div>'
           f'<div class="ctext" style="font-family:Sora;font-weight:800;font-size:{F["body"] + 10}px">{escape(nx["title"])}</div></div>') if nx else ""
    site = (f'<div class="card"{at(sc.get("site", 2))}><div class="chead">CODE · JAVA · PYTHON · C++ · JAVASCRIPT</div>'
            f'<div style="font-family:Sora;font-weight:800;font-size:{F["body"] + 18}px;letter-spacing:-1px;{U.GOLDTXT}">onehintaway.com</div></div>')
    cols = 1 if fmt == "short" else 2
    return head(sc, F) + f'<div class="grid" style="grid-template-columns:repeat({cols},1fr)">{pr}{nxt}{site}</div>'

THUMB = ('<svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#CBE6FB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
         '<path d="M7 10v11H4V10z"/><path d="M7 10l4-7c1.5 0 2.5 1 2.5 2.5V9h5.2a2 2 0 0 1 2 2.3l-1.3 8A2 2 0 0 1 17.4 21H7"/></svg>')
BELL = ('<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#1A1406" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.9 1.9 0 0 0 3.4 0"/></svg>')

def lay_outro(sc, F, fmt):
    big = 230 if fmt == "long" else 260
    logo = U.LOGO.replace('width="30" height="30"', f'width="{big}" height="{big}"')
    btn = "display:inline-flex;align-items:center;gap:16px;padding:22px 40px;border-radius:999px;font-family:Sora;font-weight:800;font-size:44px"
    return (f'<div class="center">'
            f'<div data-at="0" data-fx="pop" style="filter:drop-shadow(0 0 60px rgba(244,207,110,.28))">{logo}</div>'
            f'<div data-at="0.25" style="margin-top:34px;font-family:Sora;font-weight:800;font-size:{F["title"] + 10}px;letter-spacing:-2px;{U.GOLDTXT}">One Hint Away</div>'
            f'<div class="lead" data-at="L0" style="margin-top:26px;font-size:{F["body"] + 4}px;text-align:center">{rich(sc["text"])}</div>'
            f'<div style="margin-top:44px;display:flex;gap:26px;flex-wrap:wrap;justify-content:center">'
            f'<div data-at="L0+0.5" data-fx="pop" style="{btn};background:#1C3044;border:2px solid #7FB0DA;color:#CBE6FB">{THUMB}Like</div>'
            f'<div data-at="L0+1.3" data-fx="pop" style="{btn};background:{U.GOLDGRAD};color:#1A1406">{BELL}Subscribe</div></div></div>')

BUILD = {"outro": lay_outro, "title": lay_title, "big": lay_big, "list": lay_list, "table": lay_table, "boxes": lay_boxes, "compare": lay_compare,
         "pause": lay_pause, "end": lay_end}


# ------------------------------------------------------------------ checks
def check(spec, fmt, errors, warns):
    part = spec[fmt]
    if fmt != "long" and not part.get("kind"):
        errors.append(f"{fmt}: a Short needs a kind: trap, hack or booster")
    scenes = part["scenes"]
    ids = [s["id"] for s in scenes]
    if len(ids) != len(set(ids)):
        errors.append(f"{fmt}: scene ids repeat")
    texts = [part.get("title", ""), spec["youtube"]["title"] if fmt == "long" else part.get("title", "")]
    total, tagged = 0, 0
    for si, sc in enumerate(scenes):
        where = f"{fmt}/{sc['id']}"
        if sc["layout"] not in LAYOUTS:
            errors.append(f"{where}: unknown layout {sc['layout']}")
        for k in sc:
            if k not in KEYS:
                errors.append(f"{where}: unknown field {k}")
        say = lines_of(sc)
        if not say and sc["layout"] != "pause":
            errors.append(f"{where}: no narration")
        for i, l in enumerate(say):
            total += 1; tagged += bool(l.get("tone"))
            if l.get("tone") and l["tone"] not in E.TONES:
                errors.append(f"{where} line {i}: unknown tone {l['tone']}")
            if SPOKEN_BAD.search(l["say"]):
                errors.append(f"{where} line {i}: write symbols out for the voice and put the written form in 'show': {l['say']!r}")
            if len(l["say"].split()) > 32:
                errors.append(f"{where} line {i}: {len(l['say'].split())} words; split it (32 at most)")
            texts.append(l.get("show", l["say"]))
            heard = l["say"] + " | " + l.get("show", "")
            if si == 0 and HYPE.search(heard):
                errors.append(f"{where}: hook uses {HYPE.search(heard).group(0)!r}")
            elif HYPE.search(heard):
                warns.append(f"{where} line {i}: {HYPE.search(heard).group(0)!r}")
        n = len(say)
        def ref(i, what):
            if isinstance(i, int) and not 0 <= i < max(n, 1):
                errors.append(f"{where}: {what} points at line {i}, the scene has {n}")
        for it in sc.get("items", []):
            ref(it.get("at", 0), "item")
        for st in sc.get("states", []):
            ref(st["at"], "state")
        for r in sc.get("at", []) if isinstance(sc.get("at"), list) else []:
            ref(r, "row")
        if sc["layout"] == "table" and isinstance(sc.get("rows"), list):
            for r in sc["rows"]:
                if len(r) != len(sc["head"]):
                    errors.append(f"{where}: a row has {len(r)} cells, the head has {len(sc['head'])}")
        if sc["layout"] == "code":
            cap = 52 if fmt == "long" else 44
            if "lines" not in sc:
                errors.append(f"{where}: code scene has no lines"); continue
            for t in sc["lines"]:
                if len(t) > cap:
                    errors.append(f"{where}: code line over {cap} characters: {t!r}")
            for l in say:
                for h in l.get("hl", []):
                    if not 1 <= h <= len(sc["lines"]):
                        errors.append(f"{where}: hl {h} is not a line")
        if "`" in sc.get("title", ""):
            errors.append(f"{where}: no backticks in titles (they show as-is)")
        for t in (sc.get("title", ""), sc.get("label", "")):
            texts.append(t)
            if HYPE.search(re.sub(r"\b(EASY|MEDIUM|HARD)\b", "", t or "")):
                errors.append(f"{where}: title or label uses {HYPE.search(t).group(0)!r}")
    if spec.get("_channel", {}).get("next_video_mention") is False:
        for sc in scenes:
            if sc.get("next"):
                errors.append(f"{fmt}/{sc['id']}: no next-video card (channel.json: next_video_mention is false)")
            for l in lines_of(sc):
                if re.search(r"\bnext (video|up)\b|\bin the next\b", l["say"], re.I):
                    errors.append(f"{fmt}/{sc['id']}: mentions the next video: {l['say']!r}")
    if total and tagged / total > 0.55:
        errors.append(f"{fmt}: {tagged} of {total} lines carry a tone tag; keep it to about half at most, never every line")
    if total >= 6 and tagged / total < 0.2:
        errors.append(f"{fmt}: only {tagged} of {total} lines carry a tone tag; aim for about one in three so the voice rises and falls")
    if fmt == "long":
        if HYPE.search(spec["youtube"]["description"]):
            errors.append(f"YouTube description uses {HYPE.search(spec['youtube']['description']).group(0)!r}")
        if HYPE.search(spec["youtube"]["title"]):
            errors.append(f"YouTube title uses {HYPE.search(spec['youtube']['title']).group(0)!r}")
        if len(spec["youtube"]["title"]) > 70:
            errors.append("YouTube title over 70 characters")
        chs = [s for s in scenes if s.get("chapter")]
        if not scenes[0].get("chapter"):
            errors.append("long: the first scene needs a chapter name (YouTube chapters start at 0:00)")
        if len(chs) < 3:
            errors.append("long: YouTube needs at least 3 chapters")


# ------------------------------------------------------------------ build
CSS = """
.sc{position:absolute;visibility:hidden;color:#F5F6F8;font-family:Manrope,sans-serif;display:flex;flex-direction:column;justify-content:center;box-sizing:border-box}
.pill{align-self:flex-start;display:inline-flex;align-items:center;gap:12px;padding:10px 22px 10px 16px;border:1.5px solid #3A3F49;border-radius:999px;
  font-family:'Geist Mono',monospace;font-size:28px;font-weight:600;letter-spacing:2px;color:#A3CDF2}
.pill span{width:9px;height:9px;border-radius:50%;background:#A3CDF2;box-shadow:0 0 10px #A3CDF2}
.center .pill{align-self:center}
.ttl{font-family:Sora;font-weight:800;letter-spacing:-2px;line-height:1.08;margin-top:22px;text-wrap:balance}
.center{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;flex:1}
.lead{font-weight:600;color:#D3D7DE;line-height:1.35;text-wrap:pretty}
.bigmono{font-family:'Geist Mono',monospace;font-weight:600;color:#F5F6F8;font-size:1.1em;line-height:1.4;white-space:pre;text-align:left}
.biggold{font-family:Sora;font-weight:800;letter-spacing:-1.5px;color:#FFE3A0;font-size:1.35em;line-height:1.15}
b.g{color:#FFE3A0;font-weight:800} code{font-family:'Geist Mono',monospace;font-weight:600;color:#CBE6FB;font-size:.92em}
.grid{display:grid;gap:26px;margin-top:40px;align-content:start}
.card{background:linear-gradient(180deg,#1C1F25 0%,#15171C 100%);border:2px solid #2B2F37;border-radius:28px;padding:30px 36px;box-shadow:0 18px 40px rgba(0,0,0,.35)}
.card.acc{box-shadow:inset 5px 0 0 0 currentColor,0 18px 40px rgba(0,0,0,.35)}
.chead{font-family:'Geist Mono',monospace;font-size:26px;font-weight:600;letter-spacing:2.5px;color:#A3CDF2;margin-bottom:12px}
.ctext{font-weight:600;color:#E3E6EA;line-height:1.35}
.cmono{font-family:'Geist Mono',monospace;font-weight:500;color:#E3E6EA;white-space:pre;line-height:1.45}
.res{font-family:'Geist Mono',monospace;font-weight:600;margin-top:14px}
.tbl{display:grid;margin-top:34px;border:1.5px solid #2B2F37;border-radius:20px;overflow:hidden;background:#121418}
.th{font-family:'Geist Mono',monospace;font-size:26px;font-weight:600;letter-spacing:2px;color:#A2A8B3;padding:16px 24px;background:#1A1D23;border-bottom:1.5px solid #2B2F37}
.td{font-weight:600;color:#E3E6EA;padding:13px 28px;border-bottom:1px solid #22252C;line-height:1.3}
.tbl.compact .td{padding:14px 16px;font-size:.7em;white-space:nowrap} .tbl.compact .th{padding:14px 16px;font-size:22px} .td.m{font-family:'Geist Mono',monospace;font-weight:500;color:#CBE6FB}
.code{margin-top:30px;background:#0F1115;border:1.5px solid #2B2F37;border-radius:22px;padding:20px 0;font-family:'Geist Mono',monospace;font-weight:500}
.cl{display:flex;gap:26px;padding:3px 30px;white-space:pre;line-height:1.45;color:#E3E6EA}
.cl i{font-style:normal;color:#4A4F59;width:1.4em;text-align:right;flex:none}
.cl.on{background:rgba(244,207,110,0.10);box-shadow:inset 4px 0 0 #F4CF6E} .cl.on span{color:#FFE3A0}
.cl.bad{background:rgba(229,115,107,0.14);box-shadow:inset 4px 0 0 #E5736B} .cl.bad span{color:#FFC2BC}
.stack{display:grid} .stack>*{grid-area:1/1}
.row{display:flex;gap:18px;justify-content:center}
.under{display:flex;gap:18px;justify-content:center;margin-top:12px;font-family:'Geist Mono',monospace;font-size:28px;color:#6B717C;text-align:center}
.bx{border-radius:20px;border:3px solid;display:flex;align-items:center;justify-content:center;font-family:'Geist Mono',monospace;font-weight:600;box-sizing:border-box;box-shadow:0 10px 24px rgba(0,0,0,.35)}
.bx.plain{background:#16181D;border-color:#3D424C;color:#E6E8EC} .bx.gold{background:#3A2E15;border-color:#DDB25A;color:#FFE3A0}
.bx.steel{background:#1C3044;border-color:#7FB0DA;color:#CBE6FB} .bx.dim{background:#111215;border-color:#23262C;color:#4A4F59}
.bx.arrow{background:none;border-color:transparent;box-shadow:none;color:#6B717C} .bx.red{background:#3A1A18;border-color:#E5736B;color:#FFC2BC}
#caps{position:absolute;text-align:center;font-family:Manrope,sans-serif;font-weight:800;text-shadow:0 4px 18px rgba(0,0,0,.7)}
#caps .w{color:rgba(245,246,248,.40)} #caps .said{color:#F5F6F8} #caps .now{color:#F4CF6E} #caps .code{font-family:'Geist Mono',monospace;font-weight:600}
"""

EXTRA_JS = r"""
window.codeHL = function(local, s){ let on = [], bad = [];
  for (const h of (s.hl || [])) if (local >= h.t) { on = h.n; bad = h.bad; }
  document.querySelectorAll('#sc_' + s.id + ' .cl').forEach(el => { const n = Number(el.dataset.n);
    el.classList.toggle('on', on.includes(n) && !bad.includes(n)); el.classList.toggle('bad', bad.includes(n)); }); };
window.drawExtra = function(t){
  for (const s of window.__D.scenes) { if (s.cues.count === undefined) continue;
    const el = document.getElementById('sc_' + s.id); const cd = el && el.querySelector('.cd'); if (!cd) continue;
    const u = t - s.t0 - s.cues.count, n = Math.max(1, 2 - Math.floor(Math.max(0, u)));
    cd.querySelector('.num').textContent = u >= 2 ? 'Go' : n;
    cd.querySelector('.ring').setAttribute('stroke-dashoffset', String(402 * Math.min(1, Math.max(0, u / 2)))); }
};
"""

def build(spec, fmt, voice, speed=1.0):
    F = FMT[kind(fmt)]; part = spec[fmt]; fk = kind(fmt)
    vid = E.Video(f"{spec['number']:02d}-{spec['slug']}-{fmt}", F["W"], F["H"], voice=voice, speed=speed, cap_chars=F["cap_chars"])
    kit_v = kit_tl = None
    x, y, w, h = F["sc"]
    html = []
    scenes = list(part["scenes"])
    out = spec.get("_channel", {}).get("outro", {})
    if out.get("long" if fk == "long" else "shorts"):
        scenes.append({"id": "outro", "layout": "outro", "text": out["text"], "say": [{"say": out["say"], "tone": "warm"}], "post": 1.6})
    part["_scenes"] = scenes
    for sc in scenes:
        say = lines_of(sc)
        if sc["layout"] == "kit":
            if kit_tl is not None:
                raise SystemExit(f"{fmt}/{sc['id']}: one kit scene per video")
            _, _, kit_v, kit_tl = K.load(sc.get("from_post", spec.get("post")))
            n = len(kit_tl["states"])
            bad = [k for k in sc["steps"] if not 0 <= int(k) < n]
            if bad:
                raise SystemExit(f"{fmt}/{sc['id']}: steps {bad} do not exist; the post's video has {n} steps (0 to {n - 1})")
            html.append(f'<div class="sc" id="sc_{sc["id"]}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;font-size:{F["body"]}px;justify-content:flex-start">{head(sc, F)}</div>')
            s = vid.kit_scene(sc["id"], kit_tl, {int(k): v for k, v in sc["steps"].items()}, pre=0.6, post=sc.get("post", 0.9), slow=sc.get("slow", 1.0))
            sh = kit_tl["layout"]["height"]
            top, avail = (330, 560) if fk == "long" else (500, 800)
            sc_ = min(1.55 if fk == "long" else 1.05, avail / sh, (w + 40) / 920)
            s["kit"].update(x=round((F["W"] - 920 * sc_) / 2), y=round(top + (avail - sh * sc_) / 2), scale=round(sc_, 3))
            if sc.get("chapter"):
                s["chapter"] = sc["chapter"]
            continue
        inner = lay_code(sc, F, fk, say) if sc["layout"] == "code" else BUILD[sc["layout"]](sc, F, fk)
        html.append(f'<div class="sc" id="sc_{sc["id"]}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;font-size:{F["body"]}px">{inner}</div>')
        kw = {}
        if sc["layout"] == "pause":
            kw = dict(countdown=2, cd_step=1.0)
        s = vid.scene(sc["id"], say, post=sc.get("post", 0.6), **kw)
        if sc.get("chapter"):
            s["chapter"] = sc["chapter"]
        if sc["layout"] == "code":
            s["hl"] = [{"t": s["cues"][f"L{i}"], "n": l.get("hl", []), "bad": l.get("bad", [])} for i, l in enumerate(say) if "hl" in l or "bad" in l]
            s["onDraw"] = "codeHL"
    vid.extra.update({"music": 0.035})
    body = (f'<div style="position:absolute;inset:0;background-color:#08090B;background-image:radial-gradient(1300px 900px at 50% 35%, #181B21 0%, rgba(24,27,33,0) 70%)"></div>'
            f'<div style="position:absolute;{F["logo"]};display:flex;align-items:center;gap:12px;opacity:.75">{U.LOGO}'
            f'<div style="font-family:{U.MONO};font-size:22px;font-weight:600;letter-spacing:4px;color:#A2A8B3">ONE HINT AWAY</div></div>'
            + "".join(html)
            + (f'<div id="kitwrap" style="position:absolute;left:0;top:0;transform-origin:0 0;opacity:0">{K.stage_div(kit_v)[0]}</div>' if kit_tl else "")
            + f'<div id="caps" style="{F["caps"]}"></div>')
    return vid, E.page(F["W"], F["H"], body, CSS, vid.data(), kit_v=kit_v, kit_tl=kit_tl, extra_js=EXTRA_JS)

CHECK_JS = r"""
([W, H, capTop, topSafe]) => {
  const bad = [];
  for (const s of window.__D.scenes) {
    const el = document.getElementById('sc_' + s.id);
    if (getComputedStyle(el).visibility === 'hidden') continue;
    for (const e of el.querySelectorAll('*')) {
      let op = 1, p = e; while (p && p !== document.body) { op *= Number(getComputedStyle(p).opacity); p = p.parentElement; }
      if (op < 0.05) continue;
      const r = e.getBoundingClientRect(); if (!r.width || !r.height) continue;
      const txt = (e.innerText || '').trim().slice(0, 40);
      if (r.right > W - 50 || r.left < 50) bad.push(`${s.id}: off the side (${Math.round(r.left)}..${Math.round(r.right)}) ${txt}`);
      if (r.bottom > capTop - 12) bad.push(`${s.id}: runs into the captions by ${Math.round(r.bottom - capTop + 12)}px ${txt}`);
      if (r.top < topSafe) bad.push(`${s.id}: too high (${Math.round(r.top)}) ${txt}`);
      if (e.scrollWidth > e.clientWidth + 2 && getComputedStyle(e).overflow !== 'visible') bad.push(`${s.id}: text cut off ${txt}`);
    }
  }
  return [...new Set(bad)].slice(0, 12);
}
"""

def stills(vid, html, out, F):
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    bad = []
    with sync_playwright() as p:
        br = p.chromium.launch(); pg = br.new_page(viewport={"width": F["W"], "height": F["H"]})
        pg.set_content(html); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        for k, s in enumerate(vid.scenes):
            t = s["t1"] - 0.32
            pg.evaluate(f"window.draw({t})")
            pg.screenshot(path=str(out / f"scene-{k + 1:02d}-{s['id']}.png"))
            bad += pg.evaluate(CHECK_JS, [F["W"], F["H"], F["caps_top"], F["top_safe"]])
        br.close()
    return bad

def mmss(t):
    return f"{int(t // 60)}:{int(t % 60):02d}"

def summary(spec, vids):
    L = []
    for fmt, vid in vids.items():
        part = spec[fmt]
        L.append(f"== {fmt.upper()}  {mmss(vid.t)}  ({len(vid.scenes)} scenes)" + (f"  {part.get('kind', '')}: {part.get('title', '')}" if fmt != "long" else ""))
        for sc, s in zip(part.get("_scenes", part["scenes"]), vid.scenes):
            L.append(f"-- {mmss(s['t0'])} {sc['id']}" + (f"  [chapter: {sc['chapter']}]" if sc.get("chapter") else ""))
            for l in lines_of(sc):
                L.append(("   (" + l["tone"] + ") " if l.get("tone") else "   ") + l.get("show", l["say"]))
    yt = spec["youtube"]
    if "long" in vids:
        ch = "\n".join(f"{mmss(s['t0'])} {s['chapter']}" for s in vids["long"].scenes if s.get("chapter"))
        L += ["", "== YOUTUBE", "Title: " + yt["title"], "", yt["description"].replace("{CHAPTERS}", ch), "", "Tags: " + ", ".join(yt["tags"])]
    return "\n".join(L)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folders", nargs="+"); ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "build"))
    ap.add_argument("--video", help="long, short, short2..., both (long + first Short) or all"); ap.add_argument("--draft", action="store_true")
    ap.add_argument("--voice", default=None)
    a = ap.parse_args()
    failed = False
    for folder in a.folders:
        spec, errors = load(folder); warns = []
        fmts = formats(spec)
        for fmt in fmts:
            check(spec, fmt, errors, warns)
        name = f"{spec['number']:02d}-{spec['slug']}"
        if errors:
            print(f"{name}: SCRIPT FAILED"); [print("  ", e) for e in errors]; failed = True; continue
        out = Path(a.out) / name; vids = {}
        vc = spec.get("_channel", {}).get("voice", {})
        for fmt in fmts:
            vid, html = build(spec, fmt, a.voice or vc.get("name", "af_heart"), vc.get("speed", 1.0)); vids[fmt] = vid
            lo, hi = LIMITS[kind(fmt)]
            if not lo <= vid.t <= hi:
                errors.append(f"{fmt}: {vid.t:.0f}s, aim for {lo} to {hi}s")
            if fmt == "long":
                chs = [s for s in vid.scenes if s.get("chapter")]
                for c0, c1 in zip(chs, chs[1:] + [{"t0": vid.t}]):
                    if c1["t0"] - c0["t0"] < 10:
                        errors.append(f"chapter {c0['chapter']!r} is under 10 s (YouTube ignores chapters that short)")
            bad = stills(vid, html, out / fmt, FMT[kind(fmt)])
            errors += [f"{fmt} LAYOUT {b}" for b in bad]
            want = a.video in (fmt, "all") or (a.video == "both" and fmt in ("long", "short"))
            if want and not bad:
                f = vid.render(html, out, draft=a.draft); vid.srt(out / f"{vid.name}.srt"); print("  video", f)
        (out / "summary.txt").write_text(summary(spec, vids))
        for w in warns:
            print(f"  warn {w}")
        if errors:
            failed = True; print(f"{name}: FAILED"); [print("  ", e) for e in errors]
        else:
            print(f"{name}: OK " + ", ".join(f"{k} {mmss(v.t)}" for k, v in vids.items()) + f" -> {out}")
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
