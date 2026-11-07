"""Turns posts/NN-slug/post.json (+ ref.py) into slides. Templates, derived values
and the validator live here. Nothing here is written per post."""
import json
import math
import re
import runpy
from pathlib import Path

from . import ui
from .ui import esc, md, NOLIG, MONO, SORA, CARD, GOLDTXT, STEEL, GOLD, ROOT

# ---------------- templates (slide order) ----------------
TEMPLATES = {
    # 7 slides; up to 2 "extra" slides may sit between picture and template (two-topic posts)
    "concept": ["cover", "video", "story", "picture", "extra*", "template", "trap", "practice"],
    # 13 slides with 4 hints and 2 solution slides; 3-5 hints and 1-2 solution slides allowed
    "challenge": ["cover", "story", "problem", "pause", "hint+", "bridge", "video", "solution+", "closing"],
}
LIMITS = {"extra": (0, 2), "hint": (3, 5), "solution": (1, 2)}
DEFAULT_LABEL = {"video": "WATCH IT MOVE", "story": "THE STORY", "picture": "THE PICTURE", "template": "THE TEMPLATE",
                 "trap": "THE TRAP", "problem": "THE REAL PROBLEM"}
BOARD_NAME = {"cover": "Cover", "video": "Video (MP4 in the zip; this is its last frame)", "story": "Story",
              "picture": "Picture + quick check", "template": "Template", "trap": "Trap and cost", "practice": "Your turn",
              "problem": "The real problem", "pause": "Pause", "bridge": "Bridge", "closing": "Your turn"}
BANNED = [r"\b(easy|simple|simply|obviously|just)\b", r"\b\d+\s?%", r"\b(everyone|most people|the only|master|crack faang|never forget|guaranteed)\b"]
BRIDGE_LINES = ("This is a hard one, and being stuck means you were really trying.",
                "Every hint you worked through is progress you keep. Read the solution slowly, then try it again tomorrow from a blank page.")


class PostError(Exception):
    pass


# ---------------- loading + derived values ----------------
def load(folder):
    folder = Path(folder)
    post = json.loads((folder / "post.json").read_text())
    ns = {}
    if (folder / "ref.py").exists():
        ns = runpy.run_path(str(folder / "ref.py"))
    ns.setdefault("sp", lambda xs: " ".join(str(x) for x in xs))
    ns.setdefault("ls", lambda xs: "[" + ", ".join(str(x) for x in xs) + "]")
    return post, ns


def _subst(obj, ns, errors, where="post"):
    """Replace {{expr}} in every string with the value computed by ref.py."""
    if isinstance(obj, str):
        def rep(m):
            try:
                v = eval(m.group(1), dict(ns))
            except Exception as e:  # noqa
                errors.append(f"{where}: cannot compute {{{{{m.group(1)}}}}}: {e}")
                return "??"
            return " ".join(map(str, v)) if isinstance(v, (list, tuple)) else str(v)
        return re.sub(r"\{\{(.+?)\}\}", rep, obj)
    if isinstance(obj, list):
        return [_subst(x, ns, errors, where) for x in obj]
    if isinstance(obj, dict):
        return {k: _subst(v, ns, errors, f"{where}.{k}") for k, v in obj.items()}
    return obj


def expand(post):
    """Resolve the slide list against the template; returns [(type, slide)] incl. cover."""
    kind = post["kind"]
    seq = [("cover", post["cover"])] + [(s["type"], s) for s in post["slides"]]
    tpl = TEMPLATES[kind]
    i = 0
    errors = []
    for t in tpl:
        base = t.rstrip("*+")
        lo, hi = LIMITS.get(base, (1, 1))
        n = 0
        while i < len(seq) and seq[i][0] == base:
            n += 1
            i += 1
        if not (lo <= n <= hi):
            errors.append(f"template '{kind}': expected {lo}-{hi} '{base}' slide(s) here, found {n}")
    if i != len(seq):
        errors.append(f"template '{kind}': unexpected slide '{seq[i][0]}' at position {i + 1}")
    return seq, errors


def complexity_ok(expr, constraints):
    try:
        return eval(expr.replace("^", "**"), {"log": lambda x: math.log2(max(x, 2)), "sqrt": math.sqrt}, dict(constraints)) <= 1e8
    except Exception:
        return False


def _box_rows(o, kind="boxes"):
    """Every boxes/steps row anywhere inside a slide: yields (block type, row dict with 'values')."""
    if isinstance(o, dict):
        t = o.get("type", kind)
        if "values" in o and isinstance(o["values"], list):
            yield t, o
        for k, v in o.items():
            yield from _box_rows(v, "steps" if k == "rows" else t)
    elif isinstance(o, list):
        for v in o:
            yield from _box_rows(v, kind)


def validate(post, ns, seq):
    errs, warns = [], []
    kind = post["kind"]
    types = [t for t, _ in seq]
    # cover promise points at a real slide
    pt = post["cover"].get("promise_slide")
    if pt and pt not in types:
        errs.append(f"cover promise points at '{pt}', which this post doesn't have")
    for n, (t, s) in enumerate(seq, 1):
        where = f"slide {n:02d} ({t})"
        if t not in ("cover", "pause", "bridge") and n > 1 and not s.get("teaser"):
            errs.append(f"{where}: needs a 'teaser' (shown on the previous slide's footer)")
        if s.get("teaser") and len(s["teaser"]) > 34:
            errs.append(f"{where}: teaser over 34 characters")
        # "dash" draws an empty dashed slot (a gap) with no number: it must never sit on a real value
        for b, row in _box_rows(s):
            hidden = [str(row["values"][i]) for i in row.get("dash", []) if i < len(row["values"]) and str(row["values"][i]) != ""]
            if hidden:
                errs.append(f"{where}: 'dash' hides {', '.join(hidden)} in a {b} block. 'dash' is for empty slots "
                            f"(value \"\"); mark a value with gold (current pick), steel (done) or dim (out of play)")
        if t == "story" and not s.get("scene"):
            errs.append(f"{where}: story needs 'scene', an everyday situation in plain words")
        qc = s.get("quickcheck")
        if qc:
            if not qc.get("answer") or not qc.get("check"):
                errs.append(f"{where}: quick check needs 'answer' and 'check' (a ref.py expression)")
            else:
                try:
                    v = eval(qc["check"], dict(ns))
                    vs = " ".join(map(str, v)) if isinstance(v, (list, tuple)) else str(v)
                    if vs not in qc["answer"]:
                        errs.append(f"{where}: quick-check answer says '{qc['answer']}' but ref.py gives {vs}")
                except Exception as e:
                    errs.append(f"{where}: quick-check check failed: {e}")
        for b in [x for x in s.get("blocks", []) if x.get("type") == "cost"] + ([s["cost"]] if s.get("cost") else []):
            if True:
                for it in b["items"]:
                    if not re.fullmatch(r"O\(.+\)", it["value"]):
                        errs.append(f"{where}: cost value '{it['value']}' must be Big-O, like O(n²)")
        ex = s.get("example")
        if ex and "expect" in ex:
            got = eval(ex["expr"], dict(ns))
            if str(got) != str(ex["expect"]):
                errs.append(f"{where}: example returns {got}, slide says {ex['expect']}")
        for p in s.get("problems", []):
            for f in ("id", "title", "difficulty", "complexity", "constraints"):
                if f not in p:
                    errs.append(f"{where}: problem {p.get('id', '?')} missing '{f}'")
            if "complexity" in p and "constraints" in p and not p.get("partial") and not complexity_ok(p["complexity"], p["constraints"]):
                errs.append(f"{where}: LeetCode {p['id']} hint is {p['complexity']} — too slow for its limits {p['constraints']}. "
                            "Give a hint that passes, or mark it partial and say so on the slide.")
        # honest hooks
        for field in ("teaser", "title", "lead"):
            txt = (s.get(field) or "").lower()
            for pat in BANNED:
                if re.search(pat, txt):
                    errs.append(f"{where}: '{field}' uses a banned hook word ({re.search(pat, txt).group(0)})")
    used = Path(__file__).resolve().parent.parent / "used_problems.json"
    if used.exists():
        u = json.loads(used.read_text())
        for t, s in seq:
            for p in s.get("problems", []):
                prev = u.get(str(p.get("id")))
                if prev and prev != post["number"]:
                    warns.append(f"LeetCode {p['id']} was already the practice problem in post {prev}")
    return errs, warns


# ---------------- slide builders ----------------
def _wrap(n, total, inner, teaser, last=False, spacer=True):
    return f'<div style="{ROOT}">\n{ui.header(n, total)}{inner}{ui.footer(teaser, last, spacer)}</div>'


def _title_block(s, label, label_color=STEEL, mt=40):
    out = ui.pill_label(label, label_color, mt) if label else ""
    if s.get("title"):
        out += ui.h1(s["title"], 22 if label else 36)
    lead = s.get("scene") or s.get("lead")
    if lead:
        out += ui.lead(lead)
    return out


def build(post, ns, seq, video_still=None):
    """Returns list of dicts {name, title, html(inner slide div)}."""
    total = len(seq)
    kind = post["kind"]
    hints = [s for t, s in seq if t == "hint"]
    sols = [s for t, s in seq if t == "solution"]
    sol_start = 1
    out = []
    promise_n = None
    for n, (t, s) in enumerate(seq, 1):
        if t == post["cover"].get("promise_slide"):
            promise_n = n
    prev_answer = None
    hint_i = sol_i = 0
    pt = post["cover"].get("promise_slide")
    post["_promise_lines"] = sum(len(s["code"]["lines"]) for t, s in seq if t == pt and s.get("code"))
    for n, (t, s) in enumerate(seq, 1):
        nxt = seq[n][1].get("teaser", "") if n < total else ""
        if n < total and seq[n][0] == "pause":
            nxt = "Your 15 minutes"
        if n < total and seq[n][0] == "bridge":
            nxt = "Solved it, or still stuck?"
        inner = ""
        if prev_answer:
            inner += ui.answer_banner(prev_answer, 36 if kind == "concept" else 30)
        prev_answer = (s.get("quickcheck") or {}).get("answer")
        if t == "cover":
            inner = cover(post, s, n, total, promise_n)
        elif t == "video":
            inner += _title_block(s, s.get("label", DEFAULT_LABEL["video"]), mt=40 if not inner else 30)
            inner += video_still or '<div style="margin-top: 30px; height: 730px; border: 2px dashed #3A3F49; border-radius: 24px"></div>'
        elif t == "pause":
            inner += pause(post)
        elif t == "bridge":
            inner += bridge(sum(1 for tt, _ in seq[n:] if tt in ("video", "solution")))
        elif t in ("practice", "closing"):
            inner = practice(post, s, kind)
        else:
            label = s.get("label") or DEFAULT_LABEL.get(t)
            color = GOLD if t == "trap" else STEEL
            if t == "hint":
                hint_i += 1
                label = f"HINT {hint_i} OF {len(hints)}"
            if t == "solution":
                sol_i += 1
                label = "THE SOLUTION" + (f" · {sol_i} OF {len(sols)}" if len(sols) > 1 else "")
            mt = 30 if inner else (36 if kind == "challenge" else 40)
            inner += _title_block(s, label, color, mt)
            for b in s.get("blocks", []):
                inner += ui.block(b)
            if s.get("code"):
                c = s["code"]
                start = sol_start if t == "solution" else 1
                inner += ui.code_block(c["lines"], start, c.get("highlight", []), c.get("mt", 24))
                if t == "solution":
                    sol_start += len(c["lines"])
            if s.get("explain"):
                inner += f'<div style="margin-top: 28px; display: flex; flex-direction: column; gap: 14px; font-size: 32px; line-height: 44px; font-weight: 500; color: #D3D7DE; {NOLIG}"><div>{md(s["explain"])}</div>'
                if s.get("example"):
                    ex = s["example"]
                    got = ex.get("show") or ns["ls"](eval(ex["expr"], dict(ns)))
                    inner += f'<div>{esc(ex["call"])} returns <span style="color: #F4CF6E; font-weight: 700">{esc(got)}</span>.</div>'
                inner += "</div>"
            if s.get("trap"):
                inner += ui.blk_trap(s["trap"])
            if s.get("cost"):
                inner += ui.blk_cost(s["cost"])
            if s.get("quickcheck"):
                inner += ui.quickcheck(s["quickcheck"]["question"])
            for b in s.get("after", []):
                inner += ui.block(b)
            if t == "hint":
                inner += ui.try_again()
        last = n == total
        name = "Main.dc.html" if n == 1 else f"{n:02d}-{t.capitalize()}{'' if t not in ('hint', 'solution', 'extra') else (hint_i if t == 'hint' else sol_i if t == 'solution' else n)}.dc.html"
        board = s.get("board") or (f"Hint {hint_i}" if t == "hint" else f"Pseudocode {sol_i} of {len(sols)}" if t == "solution" and len(sols) > 1 else
                                   "Pseudocode + cost" if t == "solution" else s.get("label", "Extra").title() if t == "extra" else BOARD_NAME[t])
        out.append({"n": n, "type": t, "name": name, "board": f"{n:02d} {board}",
                    "html": inner if t == "cover" or t in ("practice", "closing") else _wrap(n, total, inner, nxt, last)})
        if t == "cover" or t in ("practice", "closing"):
            out[-1]["html"] = _wrap(n, total, inner, nxt, last, spacer=t != "cover")
    return out


def cover(post, c, n, total, promise_n):
    num = post["number"]
    inner = (f'<div style="position: absolute; right: -40px; top: 250px; font-family: {SORA}; font-size: 560px; line-height: 1; font-weight: 800; '
             f'letter-spacing: -30px; color: transparent; -webkit-text-stroke: 2px rgba(220,225,232,0.05)">{num}</div>\n')
    if post["kind"] == "concept":
        inner += ui.pill_label(f"POST {num} · {post['category'].upper()}", STEEL, 48)
        inner += ui.h1(c["title"], 28, ui.fit_title(c["title"], 140), 800, "-6px", "0.98")
        inner += ui.lead(c["lead"], 24, 40, 54)
        cards = ""
        for lab, key in (("USE IT WHEN", "use_it_when"), ("WHY IT MATTERS", "why_it_matters")):
            cards += (f'<div style="display: flex; flex-direction: column; gap: 8px; padding: 20px 28px; {CARD}">{ui.mlabel(lab, GOLD)}'
                      f'<div style="font-size: 34px; line-height: 44px; font-weight: 600; {NOLIG}">{md(c[key])}</div></div>')
        inner += f'<div style="margin-top: 32px; display: flex; flex-direction: column; gap: 16px">{cards}</div>\n'
    else:
        p = c["problem"]
        inner += (f'<div style="margin-top: 48px; display: flex; gap: 12px">{ui.pill_label(f"POST {num} · CHALLENGE", STEEL, 0)}'
                  f'<div style="display: flex; align-items: center; padding: 8px 18px; border: 1.5px solid #8A7444; border-radius: 999px; font-family: {MONO}; font-size: 24px; font-weight: 600; letter-spacing: 3px; color: #F4CF6E">{esc(p.get("platform", "LeetCode").upper())} {p["id"]} · {esc(p["difficulty"].upper())}</div></div>\n')
        inner += ui.h1(c["title"], 22, ui.fit_title(c["title"], 150), 800, "-6px", "0.98")
        inner += ui.lead("Can you crack it with hints?", 16, 40, 54)
        for b in c.get("blocks", []):
            inner += ui.block(b)
    promise = c["promise"].replace("{slide}", str(promise_n)).replace("{lines}", str(post.get("_promise_lines", "")))
    inner += (f'<div style="margin-top: auto; display: flex; flex-direction: column; gap: 16px">'
              f'<div style="display: flex; align-items: center; gap: 24px; padding: 24px 28px; border: 1.5px solid #8A7444; border-radius: 24px; background: linear-gradient(180deg, rgba(244,207,110,0.11) 0%, rgba(244,207,110,0.03) 100%); box-shadow: inset 0 1px 0 rgba(255,255,255,0.06)">'
              f'<div style="width: 72px; height: 72px; flex: none; display: flex; align-items: center; justify-content: center; border-radius: 50%; border: 1.5px solid #DDB25A; background: linear-gradient(180deg, #4A3B1C 0%, #261E0E 100%)">{ui.ICON_TARGET}</div>'
              f'<div style="display: flex; flex-direction: column; gap: 6px">{ui.mlabel(f"BY SLIDE {promise_n}", GOLD)}'
              f'<div style="font-family: {SORA}; font-size: 36px; line-height: 44px; font-weight: 700; letter-spacing: -0.5px">{gold_md(promise)}</div></div></div>'
              f'<div style="display: flex; gap: 12px">{meta_pill(ui.ICON_LAYERS, f"{total} slides")}{meta_pill(ui.ICON_CLOCK, post["_read_time"])}</div></div>\n')
    return inner


def gold_md(s):
    """**x** as gold gradient (cover promise style)."""
    return re.sub(r"\*\*(.+?)\*\*", lambda m: f'<span style="{GOLDTXT}">{m.group(1)}</span>', esc(s))


def meta_pill(icon, text):
    return (f'<div style="display: flex; align-items: center; gap: 10px; padding: 10px 18px; border: 1.5px solid #3A3F49; border-radius: 999px; font-family: {MONO}; '
            f'font-size: 24px; font-weight: 600; letter-spacing: 1px; color: #D3D7DE">{icon}{esc(text)}</div>')


def pause(post):
    p = post["cover"]["problem"]
    try_first = next((s.get("try_first") for s in post["slides"] if s["type"] == "pause"), "")
    return (ui.h1("Stop here.\n**Give it 15**\n**minutes.**", 120, 130, 800, "-4px", "1.02")
            + f'<div style="margin-top: 56px; padding: 24px 28px; {CARD}">{ui.mlabel(p.get("platform", "LeetCode").upper() + " " + str(p["id"]) + " · " + p["difficulty"].upper(), STEEL)}'
            f'<div style="margin-top: 8px; font-family: {SORA}; font-size: 44px; line-height: 54px; font-weight: 700">{esc(p["title"])}</div>'
            + (f'<div style="margin-top: 8px; font-size: 30px; line-height: 42px; font-weight: 500; color: #D3D7DE; {NOLIG}">{md(try_first)}</div>' if try_first else "")
            + "</div>" + ui.blk_text({"style": "big", "text": "Stuck? Swipe for hint 1."}))


def bridge(k):
    nxt = "the next slide" if k == 1 else f"the next {['', 'one', 'two', 'three', 'four'][k]} slides"
    return (ui.h1("Solved it?", 110, 120, 800, "-4px", "1.02") + ui.lead(f"That was all you. Compare your approach with {nxt}.", 24)
            + f'<div style="margin-top: 48px; padding: 30px 32px; {CARD}">{ui.mlabel("STILL STUCK?", GOLD)}'
            f'<div style="margin-top: 12px; font-size: 36px; line-height: 50px; font-weight: 600">{BRIDGE_LINES[0]}</div>'
            f'<div style="margin-top: 14px; font-size: 32px; line-height: 46px; font-weight: 500; color: #D3D7DE">{BRIDGE_LINES[1]}</div></div>')


def practice(post, s, kind):
    inner = ui.h1("Your **turn**", 28 if kind == "concept" else 36, 104 if kind == "concept" else 112, 800, "-4px", "1")
    inner += ui.tick_pills(s["learnt"])
    inner += f'<p style="margin: 14px 0 0; font-size: 32px; line-height: 44px; font-weight: 500; color: #D3D7DE">You made it to the end. Now lock it in:</p>'
    cards = ""
    if s.get("pattern"):
        cards += f'<div style="padding: 20px 28px; {CARD}">{ui.mlabel("THE PATTERN YOU USED", STEEL)}<div style="margin-top: 8px; font-family: {SORA}; font-size: 36px; line-height: 46px; font-weight: 700">{md(s["pattern"])}</div></div>'
    cards += "".join(ui.problem_card(p) for p in s["problems"])
    inner += f'<div style="margin-top: 20px; display: flex; flex-direction: column; gap: 14px">{cards}</div>'
    last = s["problems"][-1]
    inner += ui.ai_prompt(last["id"], last.get("platform", "LeetCode"))
    inner += '<div style="margin-top: 14px; font-size: 26px; line-height: 36px; font-weight: 500; color: #A2A8B3">Full code in Java, Python, C++ and JavaScript: link in bio.</div>'
    inner += f'<div style="margin-top: 18px; font-size: 34px; line-height: 44px; font-weight: 700">Next post: <span style="color: #F4CF6E; font-weight: 700">{esc(post["next_post"])}</span></div>'
    return inner


# ---------------- review summary (plain text for Jaga) ----------------
def summary(post, seq, video_seconds, warns):
    L = [f"POST {post['number']} · {post['topic']} ({post['kind']}, {len(seq)} slides, video {video_seconds:.0f}s, {post['_read_time'].lower()})", ""]
    for n, (t, s) in enumerate(seq, 1):
        head = f"{n:02d} {t.upper()}"
        if t == "cover":
            L.append(f"{head}: {s['title'].replace(chr(10), ' ').replace('**', '')} — {s.get('lead', 'Can you crack it with hints?')}")
            L.append(f"    promise: {s['promise'].replace('**', '')}")
            if post["kind"] == "concept":
                L.append(f"    use it when: {s['use_it_when']}")
                L.append(f"    why it matters: {s['why_it_matters']}")
            continue
        L.append(f"{head}: {s.get('title', '')}".rstrip(": "))
        for f in ("scene", "lead", "explain", "try_first"):
            if s.get(f):
                L.append(f"    {f}: {s[f]}")
        for b in s.get("blocks", []) + s.get("after", []):
            if b.get("text"):
                L.append(f"    {b['type']}: {b['text'].replace(chr(10), ' ')}")
        if s.get("code"):
            L.append(f"    code: {len(s['code']['lines'])} lines, key line {s['code'].get('highlight', [])}")
        if s.get("trap"):
            tr = s["trap"]
            L.append(f"    wrong: {' | '.join(tr['wrong']['code'])} -> {tr['wrong']['result']}  ({tr['wrong']['note']})")
            L.append(f"    right: {' | '.join(tr['right']['code'])} -> {tr['right']['result']}")
        if s.get("cost"):
            L.append("    cost: " + ", ".join(f"{i['label']} {i['value']}" for i in s["cost"]["items"]))
        if s.get("quickcheck"):
            L.append(f"    quick check: {s['quickcheck']['question']}  ->  {s['quickcheck']['answer']}")
        if s.get("video"):
            v = s["video"]
            L.append(f"    video: {len(v['steps'])} steps on {v['values']}; ends: {v['final'].get('caption', '')}")
        for p in s.get("problems", []):
            L.append(f"    practice: {p['difficulty']} · LeetCode {p['id']} {p['title']} — {p.get('note', '')} [{p['complexity']} vs {p['constraints']}]")
        if s.get("learnt"):
            L.append("    learnt: " + " · ".join(s["learnt"]))
        if s.get("teaser"):
            L.append(f"    (previous footer says: {s['teaser']} →)")
    L.append(f"\nNext post: {post['next_post']}")
    for w in warns:
        L.append(f"WARNING: {w}")
    return "\n".join(L)
