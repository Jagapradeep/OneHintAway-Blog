"""One Hint Away video maker: one script.json per video set -> long video + Shorts, voiced, captioned.

    youtube/scripts/NN-slug/script.json   long, short (or shorts: [...]), youtube text; optional ref.py
    python3 youtube/engine/yt.py youtube/scripts/NN-* [--video long|short|both|all] [--draft] [--out DIR]

Checks the script, builds the timeline with the real voice, renders one still per scene (its end state)
in every format, and fails on any layout overflow or broken rule. --video renders MP4s and .srt captions.
Pattern posts reuse their post kit folder: "post": "28-binary-search" gives {{...}} access to its ref.py,
"lines_from" pulls code from its slides, and the "kit" layout plays its motion video in sync with the voice.
"""
import argparse, importlib.util, json, re, sys
import numpy as np
from pathlib import Path
from html import escape
from html.parser import HTMLParser
import engine as E
import kitload as K
import viz as Z
from kitload import U

GOLD, STEEL, RED, MUTED = "#F4CF6E", "#A3CDF2", "#E5736B", "#A2A8B3"
FMT = {
    "long": dict(W=1920, H=1080, sc=(150, 110, 1620, 810), title=84, body=46, mono=38, cell=170, caps_top=948, cap_chars=34,
                 caps="left:210px;width:1500px;top:944px;font-size:42px;line-height:54px;text-wrap:balance", top_safe=96, logo="right:80px;top:44px"),
    "short": dict(W=1080, H=1920, sc=(80, 200, 920, 1110), title=88, body=48, mono=34, cell=150, caps_top=1340, cap_chars=20,
                  caps="left:100px;width:880px;top:1340px;font-size:48px;line-height:62px;text-wrap:balance", top_safe=200, logo="left:80px;top:74px"),
}
LIMITS = {"long": (90, 480), "short": (20, 58)}
HYPE = re.compile(r"\b(easy|easily|simple|simply|just|everyone|everybody|most people|almost every|every beginner|always works|guarantee\w*|crack|faang|secret|insane|never forget)\b", re.I)
SPOKEN_BAD = re.compile(r"[()\[\]²³=→<>_`{}]|\.com|\bO\(|\bn\^")
KEYS = {"together", "id", "layout", "label", "title", "say", "chapter", "kicker", "sub", "items", "head", "rows", "lines", "values", "under",
        "states", "wrong", "right", "text", "next", "practice", "cols", "mono", "note", "post", "widths", "site", "at", "checks", "compact", "lines_from", "steps", "from_post", "slow", "tag", "cell", "panels", "covered"}
LAYOUTS = {"viz", "site", "kit", "outro", "title", "big", "list", "table", "code", "boxes", "compare", "pause", "end"}


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
                    sl = slides[lf.get("n", 0)]
                    lines = list(sl["code"]["lines"] if sl.get("code") else next(b["lines"] for b in sl.get("blocks", []) if b.get("type") == "code"))
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

def spoken(sc):
    return [l for l in lines_of(sc) if "say" in l]

# ------------------------------------------------------------------ sync: what is on screen must match what is being said
_NUMW = "zero one two three four five six seven eight nine ten eleven twelve".split()
_STOPW = set("a an the and or but of to in on at is are was be been it its this that these those with for as by from "
             "not no you your we our me my they them their then there here so if into than also just can will has have do does".split())

def words(text):
    """Content words of a text, crudely stemmed (first five letters), with small numbers as words."""
    out = set()
    for w in re.findall(r"[a-z]+", E.spoken_text(re.sub(r"<[^>]+>", " ", str(text))).lower()):
        if len(w) > 2 and w not in _STOPW and w not in _NUMW:
            out.add(w[:5])
    return out

def line_words(sc):
    """Words of each narration line by its cue index (None for think/wait entries)."""
    return [words(l["say"] + " " + l.get("show", "")) if "say" in l else None for l in lines_of(sc)]

def align(texts, sc):
    """Tie each on-screen item to the line that talks about it: items keep their order, lines never go back,
    and the total word overlap is as large as possible. On a tie, items spread over separate lines, then go earlier."""
    L = [(i, w) for i, w in enumerate(line_words(sc)) if w is not None]
    if not L or not texts:
        return [0] * len(texts)
    m, n = len(L), len(texts)
    ov = [[len(words(t) & w) for _, w in L] for t in texts]
    dp = [[(10 * ov[0][k], -k) for k in range(m)]]; back = []
    for j in range(1, n):
        row, bk = [], []
        for k in range(m):
            cand = max(((dp[-1][q][0] + (1 if q < k else 0), dp[-1][q][1]), q) for q in range(k + 1))
            row.append((cand[0][0] + 10 * ov[j][k], cand[0][1] - k)); bk.append(cand[1])
        dp.append(row); back.append(bk)
    k = max(range(m), key=lambda k: dp[-1][k]); res = []
    for j in range(n - 1, -1, -1):
        res.append(L[k][0])
        if j:
            k = back[j - 1][k]
    return res[::-1]

def cues_for(sc, texts, explicit):
    """Cue of each item: its own 'at' if set, all on the first line if the scene says 'together',
    otherwise the line that talks about it."""
    if sc.get("together"):
        first = next((i for i, w in enumerate(line_words(sc)) if w is not None), 0)
        return [e if e is not None else first for e in explicit]
    auto = align(texts, sc)
    return [e if e is not None else a for e, a in zip(explicit, auto)]

class _Cued(HTMLParser):
    """Text of every element that appears on a narration line (data-at="L<i>")."""
    def __init__(self):
        super().__init__(); self.stack, self.out = [], []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs); m = re.fullmatch(r"L(\d+)", a.get("data-at") or "")
        if "cl" in (a.get("class") or "").split():      # code lines: the whole function may stay on screen
            m = None
        rec = [int(m.group(1)), ""] if m else None
        if rec:
            self.out.append(rec)
        if tag not in ("br", "img", "input", "circle", "path", "rect", "line"):
            self.stack.append(rec)
    def handle_endtag(self, tag):
        if self.stack and tag not in ("br", "img", "input", "circle", "path", "rect", "line"):
            self.stack.pop()
    def handle_data(self, d):
        for rec in self.stack:
            if rec:
                rec[1] += " " + d

class _Sections(HTMLParser):
    """Section headings (class "section") and the cues of everything under each, in page order."""
    def __init__(self):
        super().__init__(); self.out = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs); m = re.fullmatch(r"L(\d+)", a.get("data-at") or "")
        cue = int(m.group(1)) if m else None
        if "section" in (a.get("class") or "").split():
            self.out.append({"cue": cue, "items": [], "text": ""}); self._in = True
        elif self.out and cue is not None:
            self.out[-1]["items"].append(cue)
    def handle_data(self, d):
        if getattr(self, "_in", False) and self.out:
            self.out[-1]["text"] += d
    def handle_endtag(self, tag):
        self._in = False

def heading_errors(sc, inner, where):
    """A heading must arrive with the first item it introduces, not before (27 Nov 2026: "Your turn" showed
    while the voice was still on "Solved in this video")."""
    first = next((i for i, w in enumerate(line_words(sc)) if w is not None), 0)
    p = _Sections(); p.feed(inner); errs = []
    for s in p.out:
        cue = first if s["cue"] is None else s["cue"]
        if s["items"] and cue < min(s["items"]):
            errs.append(f"{where}: heading {s['text'].strip()!r} shows on line {cue}, before its first item (line {min(s['items'])})")
    return errs

def sync_errors(sc, inner, where):
    """An item must not show up before the line that talks about it, nor on a line that says nothing about it."""
    if sc.get("together"):
        return []
    lw = line_words(sc); errs = []
    p = _Cued(); p.feed(inner)
    for i, text in p.out:
        w = words(text)
        if not w or i >= len(lw) or lw[i] is None:
            continue
        ov = [len(w & x) if x is not None else -1 for x in lw]
        best = max(ov); kb = ov.index(best)
        if kb > i and best >= 2 and ov[i] == 0:      # on screen before the narration gets to it
            errs.append(f"{where}: {' '.join(text.split())[:50]!r} appears on line {i} ({(lines_of(sc)[i]['say'])[:40]!r}) "
                        f"but line {kb} talks about it; set its 'at' or reorder")
    return errs

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
    sub = f'<div class="lead" {at(sc["sub_at"] if "sub_at" in sc else cues_for(sc, [sc["sub"]], [None])[0])} style="margin-top:34px;font-size:{F["body"] + 6}px;max-width:1300px">{rich(sc["sub"])}</div>' if sc.get("sub") else ""
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
    cue = cues_for(sc, [it.get("head", "") + " " + it["text"] for it in sc["items"]], [it.get("at") for it in sc["items"]])
    for i, it in enumerate(sc["items"]):
        acc = {"gold": GOLD, "red": RED, "steel": STEEL}.get(it.get("accent"), None)
        hd = f'<div class="chead" style="color:{acc or STEEL}">{escape(it["head"])}</div>' if it.get("head") else ""
        cards.append(f'<div class="card{" acc" if acc else ""}"{at(cue[i])} style="{"border-color:" + acc if acc else ""}">'
                     f'{hd}<div class="ctext">{rich(it["text"])}</div></div>')
    return head(sc, F) + f'<div class="grid" style="grid-template-columns:repeat({cols},1fr)">{"".join(cards)}</div>'

def lay_table(sc, F, fmt):
    mono = set(sc.get("mono", []))
    w = sc.get("widths")
    gt = " ".join(w) if w else f"repeat({len(sc['head'])}, auto)"
    cells = "".join(f'<div class="th">{escape(h)}</div>' for h in sc["head"])
    ex = sc.get("at") if isinstance(sc.get("at"), list) else [sc.get("at")] * len(sc["rows"])
    cue = cues_for(sc, [" ".join(map(str, row)) for row in sc["rows"]], ex)
    for r, row in enumerate(sc["rows"]):
        a = at(cue[r])
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
    longest = max(len(t) for t in sc["lines"]) + 3
    tall = F["sc"][3] - (250 if sc.get("title") else 150) - (80 if sc.get("note") else 0)
    fs = int(min(F["mono"] * (1.3 if fmt == "short" else 1), (F["sc"][2] - (20 if fmt == "short" else 90)) / (0.6 * longest), tall / (n * 1.45 + 1.2)))
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
    cue = cues_for(sc, [" ".join([sc[k].get("head", ""), sc[k].get("text", ""), str(sc[k].get("result", ""))] + sc[k].get("code", [])) for k in ("wrong", "right")],
                   [sc[k].get("at") for k in ("wrong", "right")])
    for key, col, word in (("wrong", RED, "WRONG"), ("right", GOLD, "RIGHT")):
        c = sc[key]
        code = "".join(f'<div>{escape(t)}</div>' for t in c.get("code", []))
        out.append(f'<div class="card"{at(cue[0 if key == "wrong" else 1])} style="border-color:{col}">'
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
    def prob(p, solved=False):
        lvl = GOLD if p["level"] == "Medium" else (RED if p["level"] == "Hard" else STEEL)
        site = p.get("site", "LeetCode")
        return (f'<div class="prob{" solved" if solved else ""}"{at(p.get("at", 0))}><div class="pmeta" style="color:{lvl}">{escape(p["level"].upper())}</div>'
                f'<div class="pnum">{escape(site)} {p["id"]}</div><div class="ptitle">{escape(p["title"])}</div>'
                + (f'<div class="pnote">{rich(p["note"])}</div>' if p.get("note") else "") + '</div>')
    cov = "".join(prob(p, True) for p in sc.get("covered", []))
    pr = "".join(prob(p) for p in sc.get("practice", []))
    col = " col" if fmt == "short" else ""
    if not cov:
        return head(sc, F) + f'<div class="probs{col}" style="margin-top:18px">{pr}</div>'
    # two sections, each heading arriving with its first problem: "Your turn" waits until the solved part is done
    first = lambda ps: min((p.get("at", 0) for p in ps), default=0)
    out = head({k: v for k, v in sc.items() if k != "title"}, F)       # the section headings replace the title
    out += (f'<div class="mono-label section"{at(first(sc["covered"]))} style="margin-top:34px">SOLVED IN THIS VIDEO</div>'
            f'<div class="probs{col}" style="margin-top:18px">{cov}</div>')
    out += (f'<div class="mono-label section"{at(first(sc.get("practice", [])))} style="margin-top:44px">YOUR TURN</div>'
            f'<div class="probs{col}" style="margin-top:18px">{pr}</div>')
    return out

def lay_site(sc, F, fmt):
    return (f'<div class="center">'
            f'<div class="mono-label" data-at="0">EVERY LINE OF CODE, AND MORE</div>'
            f'<div data-at="0.15" data-fx="pop" style="margin-top:28px;font-family:Sora;font-weight:800;font-size:{120 if fmt == "long" else 104}px;letter-spacing:-3px;{U.GOLDTXT}">onehintaway.com</div>'
            f'<div data-at="L0" style="margin-top:34px;display:flex;gap:16px;flex-wrap:wrap;justify-content:center">'
            + "".join(f'<span class="chip">{c}</span>' for c in sc.get("items", ["Java", "Python", "C++", "JavaScript", "Notes", "Practice links"]))
            + '</div></div>')

def lay_outro(sc, F, fmt):
    logo = U.LOGO.replace('width="30" height="30"', 'width="76" height="76"')
    lines = "".join(f'<div class="o-line" data-at="L0{"+0.6" if k else ""}">{escape(t)}</div>' for k, t in enumerate(sc["text"].split("\n")))
    return (f'<div class="center">'
            f'<div data-at="0" data-fx="pop" style="display:flex;align-items:center;gap:22px">{logo}'
            f'<div style="font-family:Sora;font-weight:800;font-size:{F["title"] - 8}px;letter-spacing:-2px;color:#F5F6F8">One Hint Away</div></div>'
            f'<div data-at="0.3" data-fx="none" style="margin:44px 0 36px;width:120px;height:2px;background:{GOLD};opacity:.55"></div>'
            f'{lines}</div>')

def lay_viz(sc, F, fmt):
    """The problem as a picture: an array whose cells change colour, gain arcs and pointers as the voice speaks."""
    w, h = F["sc"][2], F["sc"][3]
    panels = sc.get("panels", [])
    side = bool(panels) and fmt == "long"                 # long videos: code cards on the left, the picture on the right
    rx0, rw = (700, w - 700) if side else (0, w)
    vals = sc["values"]; n = len(vals)
    cell = sc.get("cell") or int(min(F["cell"] if not side else 150, (rw - 16 * (n - 1)) / n)); gap = 16
    tot = n * cell + (n - 1) * gap; x0 = rx0 + (rw - tot) / 2
    # arcs (and pair sweeps) rise above the cells: give them room, and keep them clear of the tag and title
    pairs = [tuple(a[:2]) for st in sc["states"] for a in st.get("arcs", [])] + [tuple(p) for st in sc["states"] for p in st.get("sweep", {}).get("pairs", [])]
    peak = max([min(cell * 2.2, 40 + abs(b - a) * (cell + gap) * 0.32) for a, b in pairs], default=0)
    top_used = (215 if sc.get("title") else 0) + (100 if sc.get("tag") else 0)
    cy = max(h * (0.5 if not sc.get("title") else 0.56), top_used + (min(peak, 220) + 40 if peak else 40) + cell / 2)
    room = cy - cell / 2 - 10 - top_used - 30
    ah = round(min(1.0, room / peak), 3) if peak else 1.0
    if panels and not side:                                   # Shorts: cards go under the picture
        cy = min(cy, h * 0.42)
    sc["_viz"] = {"cell": cell, "gap": gap, "x": rx0 + rw / 2, "y": round(cy - cell / 2), "ah": ah}
    out = head(sc, F) if sc.get("title") else ""
    if sc.get("tag"):
        out += (f'<div class="vtag" data-at="0" style="position:absolute;left:{rx0}px;width:{rw}px;top:{(215 if sc.get("title") else 0) + 15}px;text-align:center;'
                f'font-family:{U.MONO};font-weight:600;font-size:{56 if fmt == "long" else 52}px;color:#F5F6F8">{rich(sc["tag"])}</div>')
    if sc.get("under"):
        for k, u in enumerate(sc["under"]):
            out += (f'<div data-at="0" data-fx="none" style="position:absolute;left:{round(x0 + k * (cell + gap))}px;width:{cell}px;top:{round(cy + cell / 2 + 16)}px;'
                    f'text-align:center;font-family:{U.MONO};font-size:26px;color:#6B717C">{escape(str(u))}</div>')
    if panels:
        cards = ""
        for pn in panels:
            col = {"red": RED, "gold": GOLD}.get(pn.get("accent"), STEEL)
            lines = "".join(f'<div style="color:{RED if k in pn.get("bad", []) else (GOLD if k in pn.get("good", []) else "#E3E6EA")}">{escape(c)}</div>'
                            for k, c in enumerate(pn["code"]))
            veil = (f'<div data-at="L{pn["dim_at"]}" data-fx="none" style="position:absolute;inset:0;border-radius:28px;background:rgba(8,9,11,.62)"></div>'
                    if "dim_at" in pn else "")
            cards += (f'<div class="card" data-at="L{pn.get("at", 0)}" data-fx="rise" style="position:relative;border-color:{col};padding:20px 28px">'
                      f'<div class="chead" style="color:{col}">{escape(pn["head"])}</div><div class="cmono" style="font-size:.78em">{lines}</div>'
                      + (f'<div class="res" style="color:{col};font-size:.78em">{rich(pn["result"])}</div>' if pn.get("result") else "")
                      + veil + '</div>')
        top = (235 if sc.get("title") else 40) if side else round(cy + cell / 2 + 170)
        out += (f'<div style="position:absolute;left:0;width:{620 if side else w}px;top:{top}px;display:flex;flex-direction:column;gap:18px">{cards}</div>')
    notes = [st for st in sc["states"] if st.get("note")]
    for j, st in enumerate(notes):
        nxt = notes[j + 1]["at"] if j + 1 < len(notes) else None
        a = st["at"] if isinstance(st["at"], str) else f"L{st['at']}"
        u = (f' data-until="{nxt if isinstance(nxt, str) else "L" + str(nxt)}"' if nxt is not None else "")
        out += (f'<div data-at="{a}"{u} data-fx="none" style="position:absolute;left:{rx0}px;width:{rw}px;top:{round(cy + cell / 2 + 90)}px;text-align:center;'
                f'font-weight:700;font-size:{F["body"] + 2}px;color:#D3D7DE">{rich(st["note"])}</div>')
    return out

SWEEP_STEP, SWEEP_END = 0.4, 0.6     # each pair of a sweep shows at least 0.4 s; the last one rests 0.6 s

def sweep_step(sw):
    return max(SWEEP_STEP, sw.get("step", 0.45))

def anim_holds(sc):
    """How long each line must wait for an animation it starts (a sweep over pairs), so nothing is cut off."""
    holds = {}
    for st in sc.get("states", []) if sc.get("layout") == "viz" else []:
        if st.get("sweep") and isinstance(st["at"], int):
            sw = st["sweep"]
            holds[st["at"]] = max(holds.get(st["at"], 0), len(sw["pairs"]) * sweep_step(sw) + SWEEP_END)
    return holds

def viz_states(sc, scene):
    """Turn the script's states (and sweeps over pairs) into timed viz states."""
    out = []
    for st in sc["states"]:
        cue = st["at"] if isinstance(st["at"], str) else f"L{st['at']}"
        look = {}
        for name in ("steel", "gold", "dim", "red"):
            for k in st.get(name, []):
                look[k] = name
        if st.get("sweep"):
            sw = st["sweep"]; step = sweep_step(sw)   # each pair stays long enough to be seen whole
            for j, (a, b) in enumerate(sw["pairs"]):
                out.append((f"{cue}+{round(j * step, 3)}" if j else cue,
                            {"st": {**look, a: "steel", b: "steel"}, "arcs": [[a, b, sw.get("color", "steel"), 4, "full"]], "sw": True, "dur": 0.08}))
            continue
        d = {"st": look}
        if st.get("arcs"):
            d["arcs"] = [list(a) + ([] if len(a) > 2 else ["gold"]) + [5] for a in st["arcs"]]
        if st.get("ptr"):
            d["ptr"] = st["ptr"]
        out.append((cue, d))
    v = sc["_viz"]
    Z.arr(scene, "v_" + sc["id"], sc["values"], v["x"], v["y"], cell=v["cell"], gap=v["gap"], states=out, arc_h=v["ah"])
    S = scene["viz"][-1]["states"]
    sw = [d["t"] for d in S if d.get("sw")]
    errs = []
    if sw:   # a sweep must finish before the next real state; anim_holds makes the narration wait for it
        nxt = min([d["t"] for d in S if not d.get("sw") and d["t"] > min(sw)], default=1e9)
        cut = [d for d in S if d.get("sw") and d["t"] > nxt - SWEEP_STEP]
        if cut:
            errs.append(f"{sc['id']}: the sweep is cut off after {len(sw) - len(cut)} of {len(sw)} pairs; start it on a line of its own (a plain line number in 'at')")
        S[:] = [d for d in S if d not in cut]
    S.sort(key=lambda d: d["t"])
    return errs

BUILD = {"viz": lay_viz, "site": lay_site, "outro": lay_outro, "title": lay_title, "big": lay_big, "list": lay_list, "table": lay_table, "boxes": lay_boxes, "compare": lay_compare,
         "pause": lay_pause, "end": lay_end}


# ------------------------------------------------------------------ checks
def check_draft(spec, errors):
    if spec.get("_draft_notes"):
        errors.append("still a draft: work through _draft_notes, then delete it")
    left = json.dumps({k: v for k, v in spec.items() if not k.startswith("_")}).count("TODO")
    if left:
        errors.append(f"{left} TODO lines still to write")

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
        say = spoken(sc)
        if not say and sc["layout"] != "pause":
            errors.append(f"{where}: no narration")
        for i, l in enumerate(lines_of(sc)):
            if "say" not in l:
                if "think" in l and not 1.5 <= l["think"] <= 5:
                    errors.append(f"{where} line {i}: think for 1.5 to 5 seconds (wait time research: about 3)")
                continue
            total += 1; tagged += bool(l.get("tone"))
            if l.get("tone") and l["tone"] not in E.TONES:
                errors.append(f"{where} line {i}: unknown tone {l['tone']}")
            if SPOKEN_BAD.search(E.spoken_text(l["say"])):
                errors.append(f"{where} line {i}: write symbols out for the voice and put the written form in 'show': {l['say']!r}")
            if len(l["say"].split()) > 32:
                errors.append(f"{where} line {i}: {len(l['say'].split())} words; split it (32 at most)")
            cap = 88 if fmt == "long" else 58        # one caption = one whole sentence, at most two lines
            for sn in re.split(r"(?<=[.?!])\s+", E.spoken_text(l.get("show", l["say"])).strip()):
                if len(sn) > cap:
                    errors.append(f"{where} line {i}: sentence of {len(sn)} characters is too long for one caption ({cap} max): {sn[:60]!r}")
            texts.append(l.get("show", l["say"]))
            heard = l["say"] + " | " + l.get("show", "")
            if si == 0 and HYPE.search(heard):
                errors.append(f"{where}: hook uses {HYPE.search(heard).group(0)!r}")
            elif HYPE.search(heard):
                warns.append(f"{where} line {i}: {HYPE.search(heard).group(0)!r}")
        n = len(lines_of(sc))
        def ref(i, what):
            if isinstance(i, int) and not 0 <= i < max(n, 1):
                errors.append(f"{where}: {what} points at line {i}, the scene has {n}")
        for it in sc.get("items", []):
            ref(it.get("at", 0), "item")
        for st in sc.get("states", []):
            ref(st["at"], "state") if isinstance(st["at"], int) else None
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
            for l in lines_of(sc):
                for h in l.get("hl", []) + l.get("bad", []):
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
            for l in spoken(sc):
                if re.search(r"\bnext (video|up)\b|\bin the next\b", l["say"], re.I):
                    errors.append(f"{fmt}/{sc['id']}: mentions the next video: {l['say']!r}")
    cap = 0.55 if fmt == "long" else 0.67      # Shorts have 3 to 5 lines: a hook question plus one reveal is normal
    if total and tagged / total > cap:
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
.card.acc{border-width:3px}
.chead{font-family:'Geist Mono',monospace;font-size:26px;font-weight:600;letter-spacing:2.5px;color:#A3CDF2;margin-bottom:12px}
.ctext{font-weight:600;color:#E3E6EA;line-height:1.35}
.cmono{font-family:'Geist Mono',monospace;font-weight:500;color:#E3E6EA;white-space:pre;line-height:1.45}
.res{font-family:'Geist Mono',monospace;font-weight:600;margin-top:14px}
.tbl{display:grid;margin-top:34px;border:1.5px solid #2B2F37;border-radius:20px;overflow:hidden;background:#121418}
.th{font-family:'Geist Mono',monospace;font-size:26px;font-weight:600;letter-spacing:2px;color:#A2A8B3;padding:16px 24px;background:#1A1D23;border-bottom:1.5px solid #2B2F37}
.td{font-weight:600;color:#E3E6EA;padding:13px 28px;border-bottom:1px solid #22252C;line-height:1.3}
.tbl.compact .td{padding:14px 16px;font-size:.7em;white-space:nowrap} .tbl.compact .th{padding:14px 16px;font-size:22px} .td.m{font-family:'Geist Mono',monospace;font-weight:500;color:#CBE6FB}
.code{overflow:hidden;margin-top:30px;background:#0F1115;border:1.5px solid #2B2F37;border-radius:22px;padding:20px 0;font-family:'Geist Mono',monospace;font-weight:500}
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
.probs{display:grid;grid-template-columns:repeat(2,1fr);gap:28px;margin-top:48px} .probs.col{grid-template-columns:1fr}
.prob{border-top:2px solid #2B2F37;padding-top:26px}
.pmeta{font-family:'Geist Mono',monospace;font-size:24px;font-weight:600;letter-spacing:3px}
.pnum{font-family:'Geist Mono',monospace;font-size:28px;color:#A2A8B3;margin-top:14px}
.ptitle{font-family:Sora;font-weight:800;font-size:1.3em;letter-spacing:-1px;margin-top:6px;color:#F5F6F8}
.prob.solved .ptitle{color:#CBE6FB}
.pnote{font-weight:600;font-size:.72em;line-height:1.4;color:#A2A8B3;margin-top:14px}
.mono-label{font-family:'Geist Mono',monospace;font-size:26px;letter-spacing:4px;color:#A2A8B3}
.chip{font-family:'Geist Mono',monospace;font-size:26px;color:#CBE6FB;border:1.5px solid #2B2F37;border-radius:999px;padding:10px 22px}
.o-line{font-weight:600;font-size:40px;color:#A2A8B3;line-height:1.5}
.think{position:absolute;left:0;right:0;bottom:24px;display:flex;align-items:center;justify-content:center;gap:16px;font-family:Sora;font-weight:700;font-size:34px;color:#A2A8B3}
#caps{position:absolute;text-align:center;font-family:Manrope,sans-serif;font-weight:800;text-shadow:0 4px 18px rgba(0,0,0,.7)}
#caps .w{color:rgba(245,246,248,.42)} #caps .said{color:#F5F6F8} #caps .now{color:#FFFFFF} #caps .code{font-family:'Geist Mono',monospace;font-weight:600}
"""

EXTRA_JS = r"""
window.codeHL = function(local, s){
  const H = s.hl || []; let k = -1;
  for (let i = 0; i < H.length; i++) if (local >= H[i].t) k = i;
  const cur = k >= 0 ? H[k] : {n: [], bad: []}, prev = k >= 1 ? H[k - 1] : {n: [], bad: []};
  const e = k < 0 ? 1 : Math.min(1, Math.max(0, (local - cur.t) / 0.45)), E = e * e * (3 - 2 * e);
  const look = (h, n) => h.bad.includes(n) ? [229,115,107,0.16,255,194,188] : (h.n.includes(n) ? [244,207,110,0.10,255,227,160] : [244,207,110,0,227,230,234]);
  document.querySelectorAll('#sc_' + s.id + ' .cl').forEach(el => { const n = Number(el.dataset.n);
    const a = look(prev, n), b = look(cur, n), m = a.map((v, i) => v + (b[i] - v) * E);
    el.classList.remove('on', 'bad');
    el.style.background = `rgba(${m[0]},${m[1]},${m[2]},${m[3]})`;
    el.style.boxShadow = m[3] > 0.005 ? `inset 4px 0 0 rgba(${m[0]},${m[1]},${m[2]},${Math.min(1, m[3] * 8)})` : 'none';
    el.querySelector('span').style.color = `rgb(${m[4]},${m[5]},${m[6]})`; }); };
window.fitCode = function(){
  document.querySelectorAll('.code').forEach(c => { let fs = parseFloat(getComputedStyle(c).fontSize);
    while (c.scrollWidth > c.clientWidth + 1 && fs > 14) { fs -= 1; c.style.fontSize = fs + 'px'; } }); };
window.drawExtra = function(t){
  for (const s of window.__D.scenes) { const host = document.getElementById('sc_' + s.id); if (!host) continue;
    host.querySelectorAll('.think').forEach(th => { const c = s.cues[th.dataset.cue]; if (c === undefined) return;
      const u = Math.min(1, Math.max(0, (t - s.t0 - c) / Number(th.dataset.dur)));
      th.querySelector('.ring').setAttribute('stroke-dashoffset', String(176 * u)); }); }
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
    vid.sync = []
    kit_v = kit_tl = None
    x, y, w, h = F["sc"]
    html = []
    scenes = list(part["scenes"])
    out = spec.get("_channel", {}).get("outro", {})
    site = spec.get("_channel", {}).get("site_frame", {})
    if fk == "long" and site.get("say"):
        scenes.append({"id": "site", "layout": "site", "say": [{"say": site["say"], "show": site.get("show", site["say"])}], "post": 1.0})
    if out.get("long" if fk == "long" else "shorts"):
        txt, say = (out["text"], out["say"]) if fk == "long" else (out.get("short_text", out["text"]), out.get("short_say", out["say"]))
        scenes.append({"id": "outro", "layout": "outro", "text": txt, "say": [{"say": say, "tone": "warm"}], "post": 1.6})
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
            top, avail = (300, 630) if fk == "long" else (480, 820)
            sc_ = min(1.55 if fk == "long" else 1.05, avail / sh, (w + 40) / 920)
            s["kit"].update(x=round((F["W"] - 920 * sc_) / 2), y=round(top + (avail - sh * sc_) / 2), scale=round(sc_, 3))
            if sc.get("chapter"):
                s["chapter"] = sc["chapter"]
            continue
        inner = lay_code(sc, F, fk, say) if sc["layout"] == "code" else BUILD[sc["layout"]](sc, F, fk)
        vid.sync += sync_errors(sc, inner, f"{fmt}/{sc['id']}") + heading_errors(sc, inner, f"{fmt}/{sc['id']}")
        for i, l in enumerate(say):
            if l.get("think"):
                until = f' data-until="L{i + 1}"' if i + 1 < len(say) else ""
                inner += (f'<div class="think" data-at="T{i}"{until} data-fx="pop" data-cue="T{i}" data-dur="{l["think"]}">'
                          '<svg width="64" height="64" viewBox="0 0 64 64"><circle cx="32" cy="32" r="28" fill="none" stroke="#2B2F37" stroke-width="5"/>'
                          f'<circle class="ring" cx="32" cy="32" r="28" fill="none" stroke="{GOLD}" stroke-width="5" stroke-linecap="round" stroke-dasharray="176" transform="rotate(-90 32 32)"/></svg>'
                          'Think</div>')
        top = ";justify-content:flex-start" if sc["layout"] == "viz" else ""
        html.append(f'<div class="sc" id="sc_{sc["id"]}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;font-size:{F["body"]}px{top}">{inner}</div>')
        kw = {"holds": anim_holds(sc)}
        if sc["layout"] == "outro":          # the ending stays quiet: no scene-change note before "Thanks for watching."
            kw["fx_in"] = None
        if sc["layout"] == "pause":
            kw = dict(countdown=2, cd_step=1.0)
        s = vid.scene(sc["id"], say, post=sc.get("post", 0.6), **kw)
        if sc.get("chapter"):
            s["chapter"] = sc["chapter"]
        if sc["layout"] == "viz":
            vid.sync += viz_states(sc, s)
        if sc["layout"] == "code":
            s["hl"] = [{"t": s["cues"][f"L{i}"], "n": l.get("hl", []), "bad": l.get("bad", [])} for i, l in enumerate(say) if "hl" in l or "bad" in l]
            s["onDraw"] = "codeHL"
    vid.extra.update({"music": 0.035})
    body = (f'<div style="position:absolute;inset:0;background-color:#08090B;background-image:radial-gradient(1300px 900px at 50% 35%, #181B21 0%, rgba(24,27,33,0) 70%)"></div>'
            f'<div style="position:absolute;{F["logo"]};display:flex;align-items:center;gap:12px;opacity:.75">{U.LOGO}'
            f'<div style="font-family:{U.MONO};font-size:22px;font-weight:600;letter-spacing:4px;color:#A2A8B3">ONE HINT AWAY</div></div>'
            + "".join(html)
            + (f'<div id="kitwrap" style="position:absolute;left:0;top:0;transform-origin:0 0;opacity:0">{K.stage_div(kit_v)[0]}</div>' if kit_tl else "")
            + (f'<div id="caps" style="{F["caps"]}"></div>' if spec.get("_channel", {}).get("burned_captions", {}).get(fk, True) else ""))
    return vid, E.page(F["W"], F["H"], body, CSS, vid.data(), kit_v=kit_v, kit_tl=kit_tl, extra_js=EXTRA_JS + Z.VIZ_JS)

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
      const cs = getComputedStyle(e);   // a box's border is one colour all round: no stripe on one side
      const sides = ['Top', 'Right', 'Bottom', 'Left'].filter(k => parseFloat(cs['border' + k + 'Width']) > 0 && cs['border' + k + 'Style'] !== 'none')
                                                    .map(k => cs['border' + k + 'Color']);
      if (new Set(sides).size > 1)
        bad.push(`${s.id}: a box border changes colour on one side ${txt}`);
      if (/inset/.test(cs.boxShadow) && !e.classList.contains('cl')) bad.push(`${s.id}: a box has a stripe on one side ${txt}`);
    }
  }
  for (const s of window.__D.scenes) { const host = document.getElementById('sc_' + s.id);
    if (!host || getComputedStyle(host).visibility === 'hidden' || !s.viz) continue;
    const ttl = host.querySelector('.ttl'); if (!ttl) continue; const tb = ttl.getBoundingClientRect().bottom;
    for (const c of host.querySelectorAll('div[style*="border-radius"]')) { const r = c.getBoundingClientRect();
      if (r.width > 40 && r.width === r.height && r.top < tb + 12) { bad.push(`${s.id}: the array overlaps the title`); break; } } }
  for (const s of window.__D.scenes) { const host = document.getElementById('sc_' + s.id);
    if (!host || getComputedStyle(host).visibility === 'hidden' || !s.viz) continue;
    const marks = [...host.querySelectorAll('.vtag, .ttl')].map(e => e.getBoundingClientRect());
    for (const p of host.querySelectorAll('svg path')) { if (Number(p.style.opacity || 1) < 0.05) continue;
      const r = p.getBoundingClientRect(); if (!r.width) continue;
      if (marks.some(m => r.top < m.bottom + 6 && r.bottom > m.top && r.left < m.right && r.right > m.left)) { bad.push(`${s.id}: an arc touches the tag or title`); break; } } }
  const kw = document.getElementById('kitwrap');
  if (kw && Number(getComputedStyle(kw).opacity) > 0.05) {
    const r = kw.querySelector('#stage').getBoundingClientRect();
    const s = window.__D.scenes.find(x => x.kit && getComputedStyle(document.getElementById('sc_' + x.id)).visibility !== 'hidden');
    const ttl = s && document.querySelector('#sc_' + s.id + ' .ttl');
    if (ttl && r.top < ttl.getBoundingClientRect().bottom + 12) bad.push(`${s.id}: the animation overlaps the title`);
    if (r.bottom > capTop - 12) bad.push(`${s ? s.id : 'kit'}: the animation runs into the captions`);
    if (r.left < 40 || r.right > W - 40) bad.push(`${s ? s.id : 'kit'}: the animation is off the side`);
  }
  return [...new Set(bad)].slice(0, 12);
}
"""

def stills(vid, html, out, F):
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("scene-*.png"):       # stills from an earlier version of the script
        old.unlink()
    bad = []
    with sync_playwright() as p:
        br = p.chromium.launch(args=E.CHROME_ARGS); pg = br.new_page(viewport={"width": F["W"], "height": F["H"]})
        pg.set_content(html); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
        pg.evaluate("window.fitCode && window.fitCode()")
        for k, s in enumerate(vid.scenes):
            t = s["t1"] - 0.32
            for v in s.get("viz", []):                     # every picture state, not only the last one
                for st in v["states"]:
                    pg.evaluate(f"window.draw({s['t0'] + st['t'] + 0.45})")
                    bad += pg.evaluate(CHECK_JS, [F["W"], F["H"], F["caps_top"], F["top_safe"]])
            pg.evaluate(f"window.draw({t})")
            pg.screenshot(path=str(out / f"scene-{k + 1:02d}-{s['id']}.png"))
            bad += pg.evaluate(CHECK_JS, [F["W"], F["H"], F["caps_top"], F["top_safe"]])
        br.close()
    return bad

def F_of(fmt):
    return FMT[kind(fmt)]

def verify(path, F, expected):
    """The finished file must be what the timeline says: size, length, frame rate, a voice track at the right loudness."""
    import subprocess
    probs = []
    pr = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                                   capture_output=True, text=True).stdout)
    v = next((x for x in pr["streams"] if x["codec_type"] == "video"), None)
    au = next((x for x in pr["streams"] if x["codec_type"] == "audio"), None)
    if not v or (v["width"], v["height"]) != (F["W"], F["H"]):
        probs.append(f"picture is not {F['W']}x{F['H']}")
    if v and v.get("r_frame_rate") != "30/1":
        probs.append(f"frame rate {v.get('r_frame_rate')}, expected 30")
    if not au or int(au.get("sample_rate", 0)) != 48000:
        probs.append("no 48 kHz audio track")
    dur = float(pr["format"]["duration"])
    if abs(dur - expected) > 0.25:
        probs.append(f"length {dur:.2f}s, timeline says {expected:.2f}s")
    ln = subprocess.run(["ffmpeg", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    import re as _re
    m = _re.findall(r"I:\s+(-?[0-9.]+) LUFS", ln)
    if not m or not -16.5 <= float(m[-1]) <= -12.5:
        probs.append(f"loudness {m[-1] if m else '?'} LUFS, expected about -14")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-"], capture_output=True).stdout   # every channel as is
    x = np.frombuffer(raw, np.float32)
    if len(x) and (np.abs(x).max() > 0.97 or (np.abs(x) > 0.95).sum() > 10):
        probs.append(f"audio clips (peak {np.abs(x).max():.2f}): distortion")
    return probs

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
                L.append(f"   [{l['think']} s to think]" if "think" in l else ("   (" + l["tone"] + ") " if l.get("tone") else "   ") + l.get("show", l["say"]))
    yt = spec["youtube"]
    if "long" in vids:
        ch = "\n".join(f"{mmss(s['t0'])} {s['chapter']}" for s in vids["long"].scenes if s.get("chapter"))
        L += ["", "== YOUTUBE", "Title: " + yt["title"], "", yt["description"].replace("{CHAPTERS}", ch), "", "Tags: " + ", ".join(yt["tags"])]
    return "\n".join(L)

def listen_list(fmt, vid, n=6):
    """The lines worth one listen: any that needed a note, then the lowest-scoring, with their time in the video."""
    log = [x for x in getattr(vid, "voice_log", []) if "text" in x]
    if not log:
        return ""
    flagged = [x for x in log if x.get("note")]
    rest = sorted([x for x in log if not x.get("note") and "mos_min" in x],
                  key=lambda x: (min(x["mos_min"] / 4.4, x.get("clarity", 1.0)), x["mos"]))[: max(0, n - len(flagged))]
    def row(x):
        sc = (f"  (naturalness {x['mos']:.2f}, worst stretch {x['mos_min']:.2f}, likeness {x['likeness']:.2f}"
              + (f", clarity {x['clarity']:.2f}" if "clarity" in x else "") + ")" if "mos" in x else "")
        return f"  {mmss(x['t'])}  {x['text'][:70]!r}{sc}" + (f"  NOTE: {x['note']}" if x.get("note") else "")
    rows = [row(x) for x in sorted(flagged + rest, key=lambda x: x["t"])]
    takes = sum(x.get("takes", 1) for x in log); kok = sum(1 for x in log if x.get("fallback"))
    return (f"\n{fmt}: listen to these {len(rows)} lines ({len(log)} lines, {takes} takes made, "
            f"{sum(1 for x in log if x.get('takes', 1) > 1)} said again, {kok} said by Kokoro):\n" + "\n".join(rows) + "\n")

def voice_report(vid):
    """Every line with its scores, to tune the bar in engine.CB from real videos."""
    rows = ["time\ttakes\tseed\tnaturalness\tworst_stretch\tlikeness\tclarity\twords_per_s\tnote\ttext"]
    for x in getattr(vid, "voice_log", []):
        rows.append("\t".join(str(x.get(k, "")) for k in ("t", "takes", "seed", "mos", "mos_min", "likeness", "clarity", "rate", "note", "text")))
    return "\n".join(rows) + "\n"

def engine_for(vc, fmt):
    """channel.json voice.engine: "kokoro", "chatterbox", or {"long": ..., "short": ...}. Kokoro when unset."""
    e = vc.get("engine", "kokoro")
    return e.get(kind(fmt), "kokoro") if isinstance(e, dict) else e

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folders", nargs="+"); ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1] / "build"))
    ap.add_argument("--video", help="long, short, short2..., both (long + first Short) or all"); ap.add_argument("--draft", action="store_true")
    ap.add_argument("--voice", default=None)
    ap.add_argument("--voice-engine", choices=["kokoro", "chatterbox"], default=None,
                    help="override channel.json voice.engine; Chatterbox videos go to build/NN-slug-chatterbox/")
    a = ap.parse_args()
    failed = False
    for folder in a.folders:
        spec, errors = load(folder); warns = []
        fmts = formats(spec)
        check_draft(spec, errors)
        for fmt in fmts:
            check(spec, fmt, errors, warns)
        name = f"{spec['number']:02d}-{spec['slug']}"
        if errors:
            print(f"{name}: SCRIPT FAILED"); [print("  ", e) for e in errors]; failed = True
            bad_dir = Path(a.out) / name; bad_dir.mkdir(parents=True, exist_ok=True)
            (bad_dir / "FAILED.txt").write_text("Script check failed, nothing rendered:\n" + "\n".join(errors) + "\n")
            continue
        vids, outs = {}, set()
        vc = spec.get("_channel", {}).get("voice", {})
        only = [f for f in fmts if a.video == f or (a.video == "both" and f in ("long", "short"))]
        for fmt in (only or fmts):           # a machine that renders one video voices only that one
            eng = a.voice_engine or engine_for(vc, fmt)
            E.set_voice_engine(eng); E.VOICE_ERRORS.clear(); E.VOICE_NOTES.clear()
            out = Path(a.out) / (name + ("-chatterbox" if eng == "chatterbox" else "")); outs.add(out)
            vid, html = build(spec, fmt, a.voice or vc.get("name", "af_heart"), vc.get("speed", 1.0)); vids[fmt] = vid
            vid.engine = eng; vid.voice_notes = list(E.VOICE_NOTES)
            errors += [f"{fmt} VOICE {e}" for e in E.VOICE_ERRORS]
            # Length and chapter targets are checked when the script is written, with Kokoro's timing. Another voice
            # paces differently, so there a miss is a warning; only YouTube's own limit (Shorts up to 3 minutes) fails.
            target = errors if eng == "kokoro" else warns
            lo, hi = LIMITS[kind(fmt)]
            if not lo <= vid.t <= hi:
                target.append(f"{fmt}: {vid.t:.0f}s, aim for {lo} to {hi}s")
            if kind(fmt) == "short" and vid.t > 180:
                errors.append(f"{fmt}: {vid.t:.0f}s is over YouTube's 3-minute limit for Shorts")
            if fmt == "long":
                chs = [s for s in vid.scenes if s.get("chapter")]
                for c0, c1 in zip(chs, chs[1:] + [{"t0": vid.t}]):
                    if c1["t0"] - c0["t0"] < 10:
                        target.append(f"chapter {c0['chapter']!r} is under 10 s (YouTube ignores chapters that short)")
            errors += [f"{fmt} SYNC {e}" for e in vid.sync]
            bad = stills(vid, html, out / fmt, FMT[kind(fmt)])
            errors += [f"{fmt} LAYOUT {b}" for b in bad]        # sync and voice faults are reported above, once
            bad = bad + vid.sync + list(E.VOICE_ERRORS)            # any of them stops the render
            want = a.video in (fmt, "all") or (a.video == "both" and fmt in ("long", "short"))
            if want and not bad:
                f = vid.render(html, out, draft=a.draft); vid.srt(out / f"{vid.name}.srt")
                problems = verify(f, F_of(fmt), vid.t)
                errors += [f"{fmt} VIDEO {x}" for x in problems]
                if problems:                     # a file that fails its check is never handed over
                    f.unlink(); (out / f"{vid.name}.srt").unlink(missing_ok=True)
                print("  video", f, "checked" if not problems else "FAILED CHECK")
        for out in outs:
            out.mkdir(parents=True, exist_ok=True)
            mine = {k: v for k, v in vids.items() if (out.name.endswith("-chatterbox")) == (v.engine == "chatterbox")}
            (out / "summary.txt").write_text(f"Voice: {', '.join(sorted({v.engine for v in mine.values()}))}\n"
                                             + ("Warnings:\n" + "\n".join(f"  {w}" for w in warns) + "\n" if warns else "")
                                             + "".join(listen_list(k, v) for k, v in mine.items()) + "\n" + summary(spec, mine))
            for k, v in mine.items():
                if getattr(v, "voice_log", None):
                    (out / f"voice-{k}.txt").write_text(voice_report(v))
            (out / "FAILED.txt").unlink(missing_ok=True)
        for w in warns:
            print(f"  warn {w}")
        if errors:
            failed = True; print(f"{name}: FAILED"); [print("  ", e) for e in errors]
            for out in outs:
                (out / "FAILED.txt").write_text("Not handed over. Fix these, then render again:\n" + "\n".join(errors) + "\n")
        else:
            print(f"{name}: OK " + ", ".join(f"{k} {mmss(v.t)} ({v.engine})" for k, v in vids.items()) + " -> " + ", ".join(map(str, sorted(outs))))
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
