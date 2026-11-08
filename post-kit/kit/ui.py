"""Graphite & Chrome v3.1 building blocks. Every style here is copied from the
approved posts (22 and 18), so a slide built from these pieces looks the same.
Nothing in this file is post-specific."""
import html as _html
import re

MONO = "'Geist Mono', ui-monospace, monospace"
SORA = "'Sora', 'Manrope', sans-serif"
NOLIG = "font-variant-ligatures: none; font-feature-settings: 'liga' 0, 'calt' 0"
CHROME = ("background-image: linear-gradient(180deg, #FFFFFF 0%, #E8EBEF 48%, #BCC2CB 100%); "
          "-webkit-background-clip: text; background-clip: text; color: transparent")
GOLDTXT = ("background-image: linear-gradient(180deg, #FFF0C2 0%, #EBC566 55%, #C99A3F 100%); "
           "-webkit-background-clip: text; background-clip: text; color: transparent")
GOLDGRAD = "linear-gradient(180deg, #FFF0C2 0%, #EBC566 55%, #C99A3F 100%)"
CARD = ("background: linear-gradient(180deg, #1C1F25 0%, #15171C 100%); border: 1.5px solid #2B2F37; "
        "border-radius: 24px; box-shadow: inset 0 1px 0 rgba(255,255,255,0.07), 0 18px 40px rgba(0,0,0,0.25)")
ROOT = ("width: 1080px; height: 1350px; box-sizing: border-box; padding: 72px 80px 64px; display: flex; text-wrap: pretty; "
        "flex-direction: column; position: relative; overflow: hidden; background-color: #08090B; "
        "background-image: radial-gradient(900px 620px at 12% -8%, #1B1E24 0%, rgba(27,30,36,0) 70%), "
        "radial-gradient(700px 500px at 100% 105%, #1B1D22 0%, rgba(27,29,34,0) 70%); color: #F5F6F8; "
        "font-family: 'Manrope', system-ui, sans-serif")
STEEL, STEEL_LT, GOLD = "#A3CDF2", "#CBE6FB", "#F4CF6E"
TEXT2, MUTED = "#D3D7DE", "#A2A8B3"

BOX = {
    "plain": "background: linear-gradient(180deg, #1A1C21 0%, #111317 100%); border: 2px solid #3D424C; color: #E6E8EC; box-shadow: inset 0 1px 0 rgba(255,255,255,0.08)",
    "gold": "background: linear-gradient(180deg, #4A3B1C 0%, #261E0E 100%); border: 2px solid #DDB25A; color: #FFE3A0; box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 0 0 4px rgba(244,207,110,0.10)",
    "steel": "background: linear-gradient(180deg, #223A52 0%, #132333 100%); border: 2px solid #7FB0DA; color: #CBE6FB; box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 0 0 4px rgba(163,205,242,0.10)",
    "dim": "background: linear-gradient(180deg, #1A1C21 0%, #111317 100%); border: 2px solid #2B2F37; color: #666C78",
}
# size: (w, h, radius, font)
BOX_SIZE = {"s": (76, 76, 16, 34), "m": (88, 88, 18, 38), "l": (112, 120, 16, 48), "xl": (150, 130, 18, 60)}

ICON_ARROW = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F4CF6E" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12h15"/><path d="M13 6l6 6-6 6"/></svg>'
ICON_SAVE = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F4CF6E" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M6 3h12v18l-6-4.5L6 21z"/></svg>'
ICON_TICK = lambda c, s=30, w="2.6": f'<svg width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex: none"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
ICON_TARGET = '<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#FFE3A0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2" fill="#FFE3A0"/></svg>'
ICON_LAYERS = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#A3CDF2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/></svg>'
ICON_CLOCK = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#A3CDF2" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>'


_NOBREAK = re.compile(r" ([−×÷≤≥→]) ")


def esc(s):
    """Escape for HTML, and keep short maths like `n − 1` or `2 × r` on one line."""
    return _NOBREAK.sub("\u00a0\\1\u00a0", _html.escape(str(s), quote=False))


def md(s, mono_inline=True):
    """Tiny inline markup: **gold**, [[steel]], `mono`, ~muted~. Newline = <br>."""
    out = esc(s)
    out = re.sub(r"\*\*(.+?)\*\*", r'<span style="color: #F4CF6E; font-weight: 700">\1</span>', out)
    out = re.sub(r"\[\[(.+?)\]\]", r'<span style="color: #CBE6FB; font-weight: 700">\1</span>', out)
    out = re.sub(r"~(.+?)~", r'<span style="color: #A2A8B3">\1</span>', out)
    if mono_inline:
        out = re.sub(r"`(.+?)`", rf'<span style="font-family: {MONO}; font-weight: 600">\1</span>', out)
    return out.replace("\n", "<br>")


def title_html(s):
    """Chrome title; **part** is gold gradient; newline breaks."""
    parts = []
    for line in str(s).split("\n"):
        segs = re.split(r"(\*\*.+?\*\*)", line)
        h = ""
        for seg in segs:
            if not seg:
                continue
            if seg.startswith("**"):
                h += f'<span style="{GOLDTXT}">{esc(seg[2:-2])}</span>'
            else:
                h += f'<span style="{CHROME}">{esc(seg)}</span>'
        parts.append(h)
    return "<br>".join(parts)


# ---------- slide chrome ----------
def header(n, total):
    return (f'<div data-chrome="header" style="flex: none; display: flex; justify-content: space-between; align-items: center">\n'
            f'<div style="display: flex; align-items: center; gap: 14px">\n'
            f'<div style="width: 22px; height: 22px; border-radius: 6px; background-image: {GOLDGRAD}"></div>\n'
            f'<div style="font-family: {MONO}; font-size: 24px; font-weight: 600; letter-spacing: 4px; color: #D3D7DE">ONE HINT AWAY</div>\n'
            f'</div>\n'
            f'<div style="font-family: {MONO}; font-size: 24px; font-weight: 600; letter-spacing: 2px; color: #A2A8B3">{n:02d} <span style="color: #3A3F49">/</span> {total:02d}</div>\n'
            f'</div>\n'
            + '<div data-chrome="progress" style="flex: none; margin-top: 20px; display: flex; gap: 8px">'
            + "".join(f'<div style="flex: 1; height: 4px; border-radius: 2px; background: {GOLDGRAD if i < n else "#2B2F37"}"></div>' for i in range(total))
            + "</div>\n")


def footer(teaser, last=False, spacer=True):
    """Fixed footer: pinned 64px from the bottom on every slide, whatever the content does.
    An invisible copy keeps its space in the flow, so bottom-anchored content stops above it."""
    pill = (f'{ICON_SAVE}Save this post' if last else f'{md(teaser, False)}{ICON_ARROW}')
    inner = (f'<div style="font-family: {MONO}; font-size: 24px; font-weight: 500; color: #A2A8B3">@onehintaway</div>\n'
             f'<div style="display: flex; align-items: center; gap: 10px; padding: 12px 24px; border: 1.5px solid #8A7444; border-radius: 999px; background: rgba(244,207,110,0.06); font-size: 28px; font-weight: 700; color: #F4CF6E; white-space: nowrap">{pill}</div>\n')
    row = "display: flex; justify-content: space-between; align-items: center; padding-top: 22px; border-top: 1.5px solid #2B2F37"
    return (('<div style="margin-top: auto"></div>\n' if spacer else '') +
            f'<div data-chrome="footer-space" aria-hidden="true" style="margin-top: 22px; visibility: hidden; flex: none; {row}">\n{inner}</div>\n'
            f'<div data-chrome="footer" style="position: absolute; left: 80px; right: 80px; bottom: 64px; {row}">\n{inner}</div>\n')


def pill_label(text, color=STEEL, mt=40):
    return (f'<div style="margin-top: {mt}px; align-self: flex-start; display: flex; align-items: center; gap: 12px; padding: 8px 18px 8px 14px; border: 1.5px solid #3A3F49; border-radius: 999px; background: rgba(255,255,255,0.02); font-family: {MONO}; font-size: 24px; font-weight: 600; letter-spacing: 3px; color: {color}">'
            f'<div style="width: 9px; height: 9px; border-radius: 50%; background: {color}; box-shadow: 0 0 10px {color}"></div>{esc(text)}</div>\n')


def h1(text, mt=22, size=92, weight=700, ls="-2.5px", lh="1.04"):
    return (f'<h1 style="margin: {mt}px 0 0; font-family: {SORA}; font-weight: {weight}; font-size: {size}px; line-height: {lh}; letter-spacing: {ls}; text-wrap: balance">{title_html(text)}</h1>\n')


def lead(text, mt=20, size=38, lh=50):
    return f'<p style="margin: {mt}px 0 0; font-size: {size}px; line-height: {lh}px; font-weight: 500; color: #D3D7DE; {NOLIG}">{md(text)}</p>\n'


def mlabel(text, color=MUTED, extra=""):
    return f'<div style="font-family: {MONO}; font-size: 24px; font-weight: 600; letter-spacing: 3px; color: {color}{extra}">{esc(text)}</div>'


# ---------- content blocks ----------
def _color(name, default=MUTED):
    return {"gold": GOLD, "steel": STEEL, "muted": MUTED, "text": "#F5F6F8"}.get(name or "", default)


def box(value, state="plain", size="l"):
    w, h, r, f = BOX_SIZE[size]
    if state == "dash":
        return f'<div style="width: {w}px; height: {h}px; flex: none; box-sizing: border-box; border-radius: {r}px; border: 2px dashed #8A7444"></div>'
    if state == "ghost":
        return f'<div style="width: {w}px; height: {h}px; flex: none"></div>'
    return (f'<div style="width: {w}px; height: {h}px; flex: none; box-sizing: border-box; border-radius: {r}px; display: flex; align-items: center; justify-content: center; '
            f'font-family: {MONO}; font-size: {f}px; font-weight: 600; {NOLIG}; {BOX[state]}">{esc(value)}</div>')


def _states(b, n):
    st = ["plain"] * n
    for name in ("gold", "steel", "dim", "dash", "ghost"):
        for i in b.get(name, []):
            st[i] = name
    for k, v in (b.get("states") or {}).items():
        st[int(k)] = v
    return st


def blk_boxes(b):
    vals = b["values"]
    n = len(vals)
    size = b.get("size") or ("l" if n <= 6 else "m" if n <= 8 else "s")
    w = BOX_SIZE[size][0]
    gap = b.get("gap", 44 if size == "l" else 16)
    st = _states(b, n)
    rows = []
    if b.get("label"):
        rows.append(f'<div style="align-self: flex-start">{mlabel(b["label"], _color(b.get("label_color")))}</div>')
    if b.get("float"):  # a box lifted above one slot, with an arrow into it
        fl = b["float"]
        cells = []
        for i in range(n):
            if i == fl["over"]:
                cells.append(f'<div style="width: {w}px; flex: none; display: flex; flex-direction: column; align-items: center; gap: 6px">{box(fl["value"], fl.get("state", "gold"), size)}'
                             f'<svg width="40" height="52" viewBox="0 0 40 52" fill="none" stroke="#F4CF6E" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 4v40"/><path d="M8 32l12 12 12-12"/></svg></div>')
            else:
                cells.append(f'<div style="width: {w}px; flex: none"></div>')
        rows.append(f'<div style="display: flex; gap: {gap}px; justify-content: center">{"".join(cells)}</div>')
    rows.append(f'<div style="display: flex; gap: {gap}px; justify-content: center">' + "".join(box(v, s, size) for v, s in zip(vals, st)) + "</div>")

    def label_row(labels, color, ls="0"):
        return (f'<div style="display: flex; gap: {gap}px; justify-content: center; font-family: {MONO}; font-size: 24px; font-weight: 600; letter-spacing: {ls}; color: {color}; {NOLIG}">'
                + "".join(f'<div style="width: {w}px; flex: none; display: flex; justify-content: center"><span style="white-space: nowrap">{esc(x)}</span></div>' for x in labels) + "</div>")
    if b.get("under"):  # free text under some boxes {"3": "smallest"}
        labs = [""] * n
        for k, v in b["under"].items():
            labs[int(k)] = v
        rows.append(label_row(labs, GOLD))
    if b.get("indexes"):
        rows.append(label_row([str(i) for i in range(n)], MUTED))
    if b.get("pointers"):
        labs = [""] * n
        for name, i in b["pointers"].items():
            labs[i] = (labs[i] + " " + name).strip()
        rows.append(label_row(labs, STEEL_LT, "2px"))
    if b.get("note"):
        rows.append(f'<div style="font-size: 30px; line-height: 42px; font-weight: 500; color: #D3D7DE; {NOLIG}">{md(b["note"])}</div>')
    inner = "".join(rows)
    if b.get("card", False):
        return f'<div style="margin-top: {b.get("mt", 28)}px; padding: 24px 28px; {CARD}; display: flex; flex-direction: column; gap: 14px">{inner}</div>'
    return f'<div style="margin-top: {b.get("mt", 32)}px; display: flex; flex-direction: column; gap: 14px">{inner}</div>'


def blk_steps(b):
    rows = []
    for r in b["rows"]:
        st = _states(r, len(r["values"]))
        rows.append(f'<div style="display: flex; align-items: center; justify-content: space-between"><div style="font-family: {MONO}; font-size: 28px; font-weight: 600; color: #D3D7DE; white-space: nowrap; {NOLIG}">{md(r.get("label", ""), False)}</div>'
                    f'<div style="display: flex; gap: 10px; flex: none">' + "".join(box(v, s, "s") for v, s in zip(r["values"], st)) + "</div></div>")
    lab = f'{mlabel(b["label"], _color(b.get("label_color")))}' if b.get("label") else ""
    return f'<div style="margin-top: {b.get("mt", 26)}px; padding: 20px 28px; {CARD}; display: flex; flex-direction: column; gap: 12px">{lab}{"".join(rows)}</div>'


def blk_bars(b):
    """Bar chart (walls). heights, water {idx: squares}, states for bars."""
    hs = b["heights"]
    n = len(hs)
    unit = b.get("unit", 64)
    inner_w = 864 if b.get("card", True) else 920
    bw = min(120, (inner_w - 40 - (n - 1) * 24) // n)
    step = bw + 24
    left0 = (inner_w - (n * step - 24)) // 2
    base = max(hs + [h + w for h, w in zip(hs, [int((b.get("water") or {}).get(str(i), 0)) for i in range(n)])]) * unit + 4
    st = _states(b, n)
    wcol = b.get("water_color", "steel")
    wst = {"steel": "background: rgba(163,205,242,0.20); border: 2px solid #7FB0DA",
           "gold": "background: rgba(244,207,110,0.22); border: 2px solid #DDB25A"}[wcol]
    els = []
    for i, h in enumerate(hs):
        x = left0 + i * step
        if h > 0:
            sty = BOX[st[i] if st[i] in BOX else "plain"]
            sty = re.sub(r"color: #[0-9A-F]+; ", "", sty)
            els.append(f'<div style="position: absolute; left: {x}px; top: {base - h * unit}px; width: {bw}px; height: {h * unit}px; box-sizing: border-box; border-radius: 14px 14px 6px 6px; {sty}"></div>')
        for k in range(int((b.get("water") or {}).get(str(i), 0))):
            els.append(f'<div style="position: absolute; left: {x + 6}px; top: {base - (h + k + 1) * unit + 4}px; width: {bw - 12}px; height: {unit - 8}px; box-sizing: border-box; border-radius: 10px; {wst}"></div>')
        vcol = {"steel": STEEL_LT, "gold": "#FFE3A0"}.get(st[i], "#E6E8EC")
        els.append(f'<div style="position: absolute; left: {x}px; width: {bw}px; text-align: center; top: {base + 10}px; font-family: {MONO}; font-size: 32px; line-height: 40px; font-weight: 600; color: {vcol}">{h}</div>')
        if b.get("indexes", True):
            els.append(f'<div style="position: absolute; left: {x}px; width: {bw}px; text-align: center; top: {base + 52}px; font-family: {MONO}; font-size: 24px; line-height: 30px; font-weight: 600; color: #A2A8B3">i = {i}</div>')
    els.append(f'<div style="position: absolute; left: {left0 - 10}px; top: {base}px; width: {n * step - 24 + 20}px; height: 2px; background: #3A3F49"></div>')
    height = base + (86 if b.get("indexes", True) else 52)
    lab = mlabel(b["label"], _color(b.get("label_color"), STEEL)) if b.get("label") else ""
    stage = f'<div style="position: relative; height: {height}px; margin-top: {12 if lab else 0}px">{"".join(els)}</div>'
    if b.get("card", True):
        return f'<div style="margin-top: {b.get("mt", 24)}px; padding: 22px 28px 18px; {CARD}">{lab}{stage}</div>'
    return f'<div style="margin-top: {b.get("mt", 24)}px">{lab}{stage}</div>'


def blk_card(b):
    lab = f'<div style="margin-bottom: 10px">{mlabel(b["label"], _color(b.get("label_color"), GOLD))}</div>' if b.get("label") else ""
    big = b.get("size") == "big"
    t = f'<div style="font-size: {34 if big else 32}px; line-height: {48 if big else 44}px; font-weight: 600; {NOLIG}">{md(b["text"])}</div>'
    sub = f'<div style="margin-top: 12px; font-size: 30px; line-height: 42px; font-weight: 500; color: #D3D7DE; {NOLIG}">{md(b["sub"])}</div>' if b.get("sub") else ""
    return f'<div style="margin-top: {b.get("mt", 28)}px; padding: 22px 28px; {CARD}">{lab}{t}{sub}</div>'


def blk_text(b):
    style = b.get("style", "note")
    if style == "note":
        return f'<p style="margin: {b.get("mt", 26)}px 0 0; font-size: 32px; line-height: 44px; font-weight: 600; color: #F5F6F8; {NOLIG}">{md(b["text"])}</p>'
    if style == "muted":
        return f'<p style="margin: {b.get("mt", 24)}px 0 0; font-size: 30px; line-height: 42px; font-weight: 500; color: #D3D7DE; {NOLIG}">{md(b["text"])}</p>'
    if style == "big":
        return f'<p style="margin: {b.get("mt", 40)}px 0 0; font-size: 38px; line-height: 52px; font-weight: 700; color: #F5F6F8; {NOLIG}">{md(b["text"])}</p>'
    raise ValueError("text style " + style)


def blk_kv(b):
    rows = ""
    for r in b["rows"]:
        c = {"steel": STEEL_LT, "gold": GOLD}.get(r[2] if len(r) > 2 else "", "#F5F6F8")
        rows += f'<div><span style="color: #A2A8B3">{esc(r[0])} =</span> <span style="color: {c}">{esc(r[1])}</span></div>'
    return f'<div style="margin-top: {b.get("mt", 28)}px; padding: 22px 28px; {CARD}; font-family: {MONO}; font-size: 32px; line-height: 50px; font-weight: 600; {NOLIG}">{rows}</div>'


def blk_equation(b):
    return f'<div style="margin-top: {b.get("mt", 16)}px; font-family: {MONO}; font-size: 34px; font-weight: 600; text-align: center; color: #F5F6F8; {NOLIG}">{md(b["text"], False)}</div>'


def blk_compare(b):
    rows = []
    for r in b["rows"]:
        val = f'<span style="{GOLDTXT}">{esc(r["value"])}</span>' if r.get("gold") else f'<span style="color: #F5F6F8">{esc(r["value"])}</span>'
        rows.append(f'<div style="padding: 22px 28px; {CARD}; display: flex; align-items: center; justify-content: space-between; gap: 20px"><div style="display: flex; flex-direction: column; gap: 6px">'
                    f'<div style="font-family: {MONO}; font-size: 36px; font-weight: 600; {NOLIG}">{esc(r["main"])}</div><div style="font-size: 28px; line-height: 36px; font-weight: 500; color: #D3D7DE">{md(r.get("sub", ""))}</div></div>'
                    f'<div style="font-family: {SORA}; font-size: 44px; font-weight: 700; white-space: nowrap">{val}</div></div>')
    return f'<div style="margin-top: {b.get("mt", 28)}px; display: flex; flex-direction: column; gap: 16px">{"".join(rows)}</div>'


def blk_trap(b):
    def side(s, good):
        border = "#7FB0DA" if good else "#2B2F37"
        code_c = STEEL_LT if good else MUTED
        lab = mlabel("RIGHT" if good else "WRONG", STEEL if good else GOLD) if b.get("labels", True) else ""
        code = "<br>".join(esc(x) for x in s["code"])
        return (f'<div style="flex: 1; display: flex; flex-direction: column; gap: 12px; padding: 24px 26px; {CARD}; border-color: {border}">{lab}'
                f'<div style="font-family: {MONO}; font-size: 26px; font-weight: 600; color: {code_c}; line-height: 36px; white-space: nowrap; {NOLIG}">{code}</div>'
                f'<div style="font-size: 28px; line-height: 38px; font-weight: 500; color: #D3D7DE; {NOLIG}">{md(s["note"])}</div>'
                f'<div style="font-family: {MONO}; font-size: 40px; line-height: 1.1; font-weight: 600; color: {code_c}; {NOLIG}">{esc(s["result"])}</div></div>')
    call = f'<div style="margin-top: 24px; font-family: {MONO}; font-size: 30px; font-weight: 600; color: #F5F6F8; {NOLIG}">{esc(b["call"])}</div>' if b.get("call") else ""
    return f'{call}<div style="margin-top: 18px; display: flex; gap: 20px">{side(b["wrong"], False)}{side(b["right"], True)}</div>'


def blk_cost(b):
    items = []
    for it in b["items"]:
        v = f'<span style="{GOLDTXT if it.get("gold") else CHROME}">{esc(it["value"])}</span>'
        note = f'<div style="font-size: 24px; line-height: 32px; font-weight: 500; color: #D3D7DE">{md(it["note"])}</div>' if it.get("note") else ""
        items.append(f'<div style="padding: 20px 22px; {CARD}; display: flex; flex-direction: column; gap: 8px"><div style="font-size: 26px; line-height: 34px; font-weight: 600; color: #A2A8B3">{esc(it["label"])}</div>'
                     f'<div style="font-family: {SORA}; font-size: 46px; line-height: 50px; font-weight: 700">{v}</div>{note}</div>')
    lab = pill_label("THE COST", STEEL, b.get("mt", 36)) if b.get("label", True) else ""
    note = f'<div style="margin-top: 22px; font-size: 28px; line-height: 38px; font-weight: 500; color: #D3D7DE; {NOLIG}">{md(b["note"])}</div>' if b.get("note") else ""
    return (f'{lab}<div style="margin-top: 20px; display: grid; grid-template-columns: repeat({len(items)}, minmax(0, 1fr)); gap: 20px">{"".join(items)}</div>{note}')


KW = {"function", "if", "else", "for", "while", "return", "from", "to", "and", "or", "not", "each", "in", "true", "false", "none", "break", "continue"}


def _code_line(line):
    indent = len(line) - len(line.lstrip(" "))
    body = line.strip()
    comment = ""
    m = re.search(r"(\s*)(//.*)$", body)
    if m:
        comment = f'<span style="display: inline-block; width: {max(1, len(m.group(1))) * 18}px"></span><span style="color: #A2A8B3">{esc(m.group(2))}</span>'
        body = body[: m.start()]
    toks = re.split(r"(\b\w+\b)", body)
    h = "".join(f'<span style="color: #A3CDF2">{t}</span>' if t in KW else esc(t) for t in toks)
    return indent * 18, h, comment


def code_block(lines, start=1, highlight=(), mt=24):
    rows = []
    for k, line in enumerate(lines):
        n = start + k
        pad, h, comment = _code_line(line)
        hl = n in highlight
        rowsty = "display: flex; gap: 22px; height: 46px; white-space: nowrap" + ("; background: rgba(244,207,110,0.08); border-radius: 10px" if hl else "")
        if hl:
            h = f'<span style="color: #F4CF6E; font-weight: 600">{esc(line.strip().split("//")[0].rstrip())}</span>'
        rows.append(f'<div style="{rowsty}"><div style="width: 40px; flex: none; text-align: right; color: #666C78">{n}</div><div style="padding-left: {pad}px">{h}{comment}</div></div>')
    return (f'<div style="margin: {mt}px 0 0; flex: none; {CARD}; overflow: hidden"><div style="display: flex; justify-content: space-between; align-items: center; padding: 14px 28px; border-bottom: 1.5px solid #2B2F37; font-family: {MONO}; font-size: 24px; font-weight: 600; letter-spacing: 3px; color: #A2A8B3"><span>PSEUDOCODE</span><span>any language</span></div>'
            f'<div style="padding: 14px 28px 16px 16px; font-family: {MONO}; font-size: 30px; line-height: 46px; font-weight: 500; color: #F5F6F8; {NOLIG}">{"".join(rows)}</div></div>')


def quickcheck(q, mt=26):
    return (f'<div style="margin-top: {mt}px; display: flex; align-items: center; gap: 24px; padding: 24px 28px; border: 1.5px solid #A88A4E; border-radius: 24px; background: linear-gradient(180deg, rgba(244,207,110,0.10) 0%, rgba(244,207,110,0.03) 100%)">'
            f'<div style="flex: 1; display: flex; flex-direction: column; gap: 6px">{mlabel("QUICK CHECK", GOLD)}<div style="font-size: 34px; line-height: 46px; font-weight: 700; {NOLIG}">{md(q)}</div></div>'
            f'<div style="width: 112px; height: 112px; flex: none; display: flex; align-items: center; justify-content: center; border-radius: 24px; border: 2px dashed #DDB25A; font-family: {SORA}; font-size: 64px; font-weight: 800; color: #F4CF6E">?</div></div>')


def answer_banner(text, mt=36):
    return (f'<div style="margin-top: {mt}px; display: flex; align-items: center; gap: 16px; padding: 18px 24px; border: 1.5px solid #4C6276; border-radius: 20px; background: rgba(163,205,242,0.07); font-size: 32px; line-height: 42px; font-weight: 600; color: #CBE6FB; {NOLIG}">'
            f'{ICON_TICK("#CBE6FB", 34)}<span>{md(text)}</span></div>\n')


def try_again(mt=26):
    return (f'<div style="margin-top: {mt}px; display: flex; align-items: center; gap: 14px; font-size: 32px; line-height: 42px; font-weight: 700; color: #F5F6F8">'
            f'<div style="width: 12px; height: 12px; border-radius: 50%; background: #F4CF6E; box-shadow: 0 0 10px #F4CF6E"></div>Try again before you swipe.</div>')


def tick_pills(items, mt=18):
    p = "".join(f'<div style="display: flex; align-items: center; gap: 10px; padding: 10px 18px 10px 14px; border: 1.5px solid #4C6276; border-radius: 999px; background: rgba(163,205,242,0.07); font-size: 26px; font-weight: 600; color: #CBE6FB; {NOLIG}">{ICON_TICK("#CBE6FB")}{esc(t)}</div>' for t in items)
    return f'<div style="margin-top: {mt}px; display: flex; flex-wrap: wrap; gap: 12px">{p}</div>'


def problem_card(p, mt=0):
    lab = f'{p["difficulty"].upper()} · {p.get("platform", "LeetCode").upper()} {p["id"]}'
    note = f'<div style="font-size: 30px; line-height: 42px; font-weight: 500; color: #D3D7DE; {NOLIG}">{md(p["note"])}</div>' if p.get("note") else ""
    return (f'<div style="padding: 20px 28px; {CARD}; display: flex; flex-direction: column; gap: 8px">{mlabel(lab, STEEL)}'
            f'<div style="font-family: {SORA}; font-size: 38px; line-height: 48px; font-weight: 700">{esc(p["title"])}</div>{note}</div>')


def ai_prompt(pid, platform="LeetCode", mt=16):
    return (f'<div style="margin-top: {mt}px; padding: 18px 28px; border: 1.5px dashed #8A7444; border-radius: 22px; background: rgba(244,207,110,0.05); display: flex; flex-direction: column; gap: 8px">{mlabel("STUCK? PASTE THIS INTO YOUR AI", GOLD)}'
            f'<div style="font-size: 30px; line-height: 42px; font-weight: 500">Give me one hint for {esc(platform)} {esc(pid)}. Don\'t show the solution unless I ask.</div></div>')


BLOCKS = {"boxes": blk_boxes, "steps": blk_steps, "bars": blk_bars, "card": blk_card, "text": blk_text, "kv": blk_kv,
          "equation": blk_equation, "compare": blk_compare, "trap": blk_trap, "cost": blk_cost,
          "html": lambda b: b["html"]}


def block(b):
    t = b["type"]
    if t == "code":
        return code_block(b["lines"], b.get("start", 1), b.get("highlight", []), b.get("mt", 24))
    if t == "quickcheck":
        return quickcheck(b["question"], b.get("mt", 26))
    if t not in BLOCKS:
        raise ValueError(f"unknown block type '{t}'")
    return BLOCKS[t](b)

# ---------- title fitting (measured with the real Sora file) ----------
_SORA_FONTS = {}


def text_width(text, size, weight=800, ls=-6.0):
    """Width in px of one line of Sora at this size, letter-spacing included."""
    import re
    from pathlib import Path
    from fontTools.ttLib import TTFont
    if weight not in _SORA_FONTS:
        f = TTFont(str(Path(__file__).resolve().parent.parent / "fonts" / f"sora-latin-{weight}-normal.woff2"))
        _SORA_FONTS[weight] = (f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm)
    cmap, hmtx, upm = _SORA_FONTS[weight]
    plain = re.sub(r"\*\*|\[\[|\]\]", "", text)
    adv = sum(hmtx[cmap.get(ord(ch), cmap.get(ord("n")))][0] for ch in plain)
    return adv * size / upm + ls * len(plain)


def fit_title(text, size, weight=800, ls=-6.0, width=920, floor=104):
    """Largest size <= `size` that keeps every line of the title on one line (never below `floor`).
    Needs `pip install fonttools brotli`; without them the size is kept and the layout check still guards."""
    lines = text.split("\n")
    try:
        text_width(lines[0], size, weight, ls)
    except ImportError:
        # a fresh workspace lacks them: install once, quietly, then measure
        import subprocess
        import sys
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "fonttools", "brotli"],
                       capture_output=True)
        _SORA_FONTS.clear()
        import importlib
        try:
            import fontTools.ttLib.woff2 as _w2
            importlib.reload(_w2)  # it remembers a failed brotli import from earlier in this run
        except ImportError:
            pass
        try:
            text_width(lines[0], size, weight, ls)
        except ImportError:
            print("note: could not install fonttools/brotli; cover title not auto-fitted")
            return size
    while size > floor and max(text_width(l, size, weight, ls) for l in lines) > width - 4:
        size -= 2
    return size
