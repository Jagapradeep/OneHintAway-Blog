"""Generic motion slide. A post describes its video as a list of steps (usually
produced by ref.py running the real algorithm); this module turns them into a
timeline, a player page with draw(t), the canvas still and the MP4.
Pacing follows design.md 6b: glide 1.2 s, equation fades in, ~1 s pause,
result, chip lands; ~3.8 s per step; final answer held 4 s, then a fade."""
import json

MOVE, EQ_IN, RES_IN, CHIP_IN, STEP = 1.2, 1.0, 2.6, 3.2, 3.8
FINAL_IN, HOLD, FADE = 1.6, 4.0, 0.8


def resolve(v):
    """Turn the step list into absolute states (ids follow cards when they move)."""
    vals = list(v["values"])
    slots = list(range(len(vals)))          # slot -> id
    idval = {i: x for i, x in enumerate(vals)}
    states, chips = [], []
    for k, s in enumerate(v["steps"] + [dict(v["final"], final=True)]):
        arc = None
        if "swap" in s:
            a, b = s["swap"]
            slots[a], slots[b] = slots[b], slots[a]
        if "move" in s:
            a, b = s["move"]
            mid = slots.pop(a)
            slots.insert(b, mid)
            arc = mid
        for slot, val in (s.get("set") or {}).items():
            idval[slots[int(slot)]] = val
        n = len(slots)
        st = ["plain"] * n
        allv = s.get("steel") == "all"
        for name in ("gold", "steel", "dim", "ghost"):
            sel = s.get(name, [])
            if sel == "all":
                sel = list(range(n))
            for i in sel:
                st[i] = name
        if allv:
            st = ["steel"] * n
        if s.get("chip") is not None:
            chips.append({"text": str(s["chip"]), "hl": bool(s.get("chip_hl")), "step": k})
        eq = s.get("eq")
        states.append({
            "slots": list(slots), "vals": {str(i): str(x) for i, x in idval.items()},
            "st": {str(slots[i]): st[i] for i in range(n)}, "arc": arc,
            "frame": s.get("frame"), "band": s.get("band"), "ptr": s.get("ptr") or {},
            "water": {str(k2): v2 for k2, v2 in (s.get("water") or {}).items()},
            "eq": ({"left": eq[0], "result": eq[1] if len(eq) > 1 else ""} if eq else None),
            "caption": s.get("caption", ""), "final": bool(s.get("final")),
        })
    return states, chips


def layout(v):
    n = len(v["values"])
    bars = v.get("mode") == "bars"
    w = min(150, (920 - (n - 1) * 26) // n)
    gap = 26
    left0 = (920 - (n * w + (n - 1) * gap)) // 2
    L = {"n": n, "w": w, "gap": gap, "left0": left0, "bars": bars, "label": v.get("stage_label", ""),
         "chipsLabel": v.get("chips_label", ""), "indexes": v.get("indexes", True)}
    allsteps = v["steps"] + [v["final"]]
    lift = any("move" in s for s in v["steps"])
    has_ptr = any(s.get("ptr") for s in v["steps"])
    has_band = any(s.get("band") for s in allsteps)
    has_chips = any(s.get("chip") is not None for s in allsteps)
    maxh = max(1, max(int(x) for x in v["values"])) if bars else 0
    unit = min(64, 300 // maxh) if bars else 0
    # natural heights of the four groups; the leftover height of the 730 px stage
    # (the size of the approved post 22/23 video stages) is shared between the gaps
    top_group = (44 if L["label"] else 0) + (70 if lift else 0)
    if bars:
        picture = maxh * unit + 10 + 40
    else:
        L["boxH"] = 130 if w >= 120 else 110
        picture = L["boxH"]
    picture += (12 + 28 if L["indexes"] else 0) + (32 if has_ptr else 0) + (14 + 42 if has_band else 0)
    eq_h, chips_h, cap_h = 80, (36 + 56 if has_chips else 0), 48
    TARGET = 730
    gaps = 3 if has_chips else 2
    natural = top_group + picture + eq_h + chips_h + cap_h
    g = max(24, (TARGET - natural) // (gaps + 1))
    y = top_group + (g if (L["label"] or lift) else g // 2)
    if bars:
        L["unit"] = unit
        L["base"] = y + maxh * unit
        L["boxTop"] = L["base"]
        L["valTop"] = L["base"] + 10
        y = L["base"] + 50
    else:
        L["boxTop"] = y
        y += L["boxH"]
    if L["indexes"]:
        L["idxTop"] = y + 12
        y += 40
    L["ptrTop"] = y
    y += 32 if has_ptr else 0
    L["bandTop"] = y + 14
    y += 56 if has_band else 0
    y += g
    L["eqTop"] = y
    y += eq_h + g
    if has_chips:
        L["chipsLabelTop"] = y
        L["chipsTop"] = y + 36
        y += chips_h + g
    L["capTop"] = y
    L["height"] = max(TARGET, y + cap_h)
    return L


def timeline(v):
    states, chips = resolve(v)
    nsteps = len(states) - 1
    duration = STEP * nsteps + FINAL_IN + HOLD + FADE
    return {"states": states, "chips": chips, "layout": layout(v), "duration": round(duration, 3),
            "T": {"MOVE": MOVE, "EQ_IN": EQ_IN, "RES_IN": RES_IN, "CHIP_IN": CHIP_IN, "STEP": STEP,
                  "FINAL_IN": FINAL_IN, "HOLD": HOLD, "FADE": FADE}}


PLAYER_JS = r"""
(function(){
const TL = window.__TL, L = TL.layout, T = TL.T, S = TL.states;
const stage = document.getElementById('stage');
const MONO = "'Geist Mono', ui-monospace, monospace", NOLIG = "font-variant-ligatures:none;font-feature-settings:'liga' 0,'calt' 0;";
const C = {plain:{t:[26,28,33],b:[17,19,23],br:[61,66,76],tx:[230,232,236],h:[0,0,0,0]},
  gold:{t:[74,59,28],b:[38,30,14],br:[221,178,90],tx:[255,227,160],h:[244,207,110,0.10]},
  steel:{t:[34,58,82],b:[19,35,51],br:[127,176,218],tx:[203,230,251],h:[163,205,242,0.10]},
  dim:{t:[26,28,33],b:[17,19,23],br:[43,47,55],tx:[102,108,120],h:[0,0,0,0]},
  ghost:{t:[26,28,33],b:[17,19,23],br:[61,66,76],tx:[230,232,236],h:[0,0,0,0]}};
const sm = x => { x = Math.min(1, Math.max(0, x)); return x*x*x*(x*(x*6-15)+10); };
const lerp = (a,b,e) => a + (b-a)*e;
const mix = (a,b,e) => a.map((v,i)=> i<3 ? Math.round(lerp(v,b[i],e)) : +lerp(v,b[i],e).toFixed(3));
const rgb = c => `rgb(${c[0]}, ${c[1]}, ${c[2]})`;
const slotX = i => L.left0 + i*(L.w+L.gap);
function el(css, text){ const d=document.createElement('div'); d.style.cssText='position:absolute;'+css; if(text!==undefined) d.textContent=text; stage.appendChild(d); return d; }
if (L.label) el(`left:0;top:0;font-family:${MONO};font-size:24px;font-weight:600;letter-spacing:3px;color:#A2A8B3;`+NOLIG, L.label);
const n = L.n, ids = Object.keys(S[0].vals);
const idx = [];
if (L.indexes) for (let i=0;i<n;i++) idx.push(el(`left:${slotX(i)}px;width:${L.w}px;top:${L.idxTop}px;text-align:center;font-family:${MONO};font-size:24px;font-weight:600;color:#A2A8B3;`+NOLIG, String(i)));
const water = [];
if (L.bars) { el(`left:${L.left0-10}px;top:${L.base}px;width:${n*(L.w+L.gap)-L.gap+20}px;height:2px;background:#3A3F49;`); }
const boxes = {}, vlab = {};
for (const id of ids) {
  boxes[id] = el(`box-sizing:border-box;width:${L.w}px;${L.bars?'border-radius:14px 14px 6px 6px;':`height:${L.boxH}px;border-radius:18px;display:flex;align-items:center;justify-content:center;font-family:${MONO};font-size:${L.w>=120?60:46}px;font-weight:600;`+NOLIG}`);
  if (L.bars) vlab[id] = el(`width:${L.w}px;text-align:center;top:${L.valTop}px;font-family:${MONO};font-size:32px;line-height:40px;font-weight:600;`+NOLIG);
}
if (L.bars) for (let i=0;i<n;i++) water.push(el(`left:${slotX(i)+6}px;width:${L.w-12}px;box-sizing:border-box;border-radius:10px;background:rgba(163,205,242,0.20);border:2px solid #7FB0DA;`));
const frame = el(`box-sizing:border-box;border:3px solid #F4CF6E;border-radius:24px;box-shadow:0 0 0 6px rgba(244,207,110,0.10);`);
const band = el(`top:${L.bandTop}px;height:4px;border-radius:2px;background:#A3CDF2;box-shadow:rgba(163,205,242,0.45) 0 0 10px;`);
const bandLab = el(`top:${L.bandTop+14}px;font-family:${MONO};font-size:24px;font-weight:600;letter-spacing:3px;color:#A3CDF2;white-space:nowrap;`+NOLIG);
const ptrNames = [...new Set(S.flatMap(s => Object.keys(s.ptr)))];
const ptr = {}; for (const p of ptrNames) ptr[p] = el(`top:${L.ptrTop}px;width:${L.w}px;text-align:center;font-family:${MONO};font-size:24px;font-weight:600;letter-spacing:2px;color:#CBE6FB;white-space:nowrap;`+NOLIG, p.toUpperCase());
function eqLayer(){ const d = el(`left:0;right:0;top:${L.eqTop}px;height:80px;display:flex;justify-content:center;align-items:center;font-family:${MONO};font-size:64px;font-weight:600;white-space:nowrap;`+NOLIG);
  d.p = document.createElement('span'); d.p.style.color='#D3D7DE'; d.r = document.createElement('span'); d.r.style.marginLeft='0.35em'; d.append(d.p, d.r); return d; }
const eqA = eqLayer(), eqB = eqLayer();
if (L.chipsLabel) el(`left:0;top:${L.chipsLabelTop}px;font-family:${MONO};font-size:24px;font-weight:600;letter-spacing:3px;color:#A2A8B3;white-space:nowrap;`+NOLIG, L.chipsLabel);
const NC = TL.chips.length, cw = NC ? Math.min(212, Math.floor((920-(NC-1)*16)/NC)) : 0;
const chips = TL.chips.map((c,i) => el(`top:${L.chipsTop}px;left:${i*(cw+16)}px;width:${cw}px;height:56px;box-sizing:border-box;border-radius:12px;display:flex;align-items:center;justify-content:center;font-family:${MONO};font-size:${cw>=180?28:24}px;font-weight:600;white-space:nowrap;`+NOLIG+(c.hl?'background:linear-gradient(180deg,#4A3B1C 0%,#261E0E 100%);border:1.5px solid #DDB25A;color:#FFE3A0;':'background:linear-gradient(180deg,#1A1C21 0%,#111317 100%);border:1.5px solid #3D424C;color:#E6E8EC;'), c.text));
function capLayer(){ return el(`left:0;right:0;top:${L.capTop}px;font-family:Manrope,sans-serif;font-size:38px;line-height:48px;font-weight:700;white-space:nowrap;`); }
const capA = capLayer(), capB = capLayer();
const fit = d => { let f = 64; d.style.fontSize = f+'px'; while (d.scrollWidth > 920 && f > 36) { f -= 2; d.style.fontSize = f+'px'; } };
function setEq(d, eq, final){ const key = eq ? eq.left+'|'+eq.result+'|'+final : ''; if (d.key === key) return; d.key = key;
  d.p.textContent = eq ? eq.left : ''; d.r.textContent = eq ? eq.result : '';
  d.r.style.cssText = 'margin-left:0.35em;' + (final ? 'color:#CBE6FB;' : "background-image:linear-gradient(180deg,#FFF0C2 0%,#EBC566 55%,#C99A3F 100%);-webkit-background-clip:text;background-clip:text;color:transparent;");
  if (!eq || !eq.result) d.r.style.marginLeft = '0'; fit(d); }
const sig = [];
const r1 = x => Math.round(x*2)/2, r2 = x => Math.round(x*100)/100;
window.DURATION = TL.duration;
window.draw = function(t){
  sig.length = 0;
  const N = S.length - 1;
  let k = Math.min(N, Math.floor(t / T.STEP)), u = t - k*T.STEP;
  if (t >= N*T.STEP) { k = N; u = t - N*T.STEP; }
  const S1 = S[k], S0 = k ? S[k-1] : null;
  const moveDur = S1.final ? T.FINAL_IN : T.MOVE;
  const e = sm(u / moveDur);
  const intro = k === 0 ? sm(u / 0.8) : 1;
  const fade = 1 - sm((t - (TL.duration - T.FADE)) / T.FADE);
  stage.style.opacity = r2(fade); sig.push(r2(fade));
  for (const id of ids) {
    const s1 = S1.slots.indexOf(+id), s0 = S0 ? S0.slots.indexOf(+id) : s1;
    const x = lerp(slotX(s0), slotX(s1), e);
    const lift = (S1.arc === +id) ? Math.sin(Math.PI*e) * 70 : 0;
    const a = C[S0 ? S0.st[id] : S1.st[id]], b = C[S1.st[id]];
    const top = mix(a.t,b.t,e), bot = mix(a.b,b.b,e), br = mix(a.br,b.br,e), tx = mix(a.tx,b.tx,e), h = mix(a.h,b.h,e);
    const ghostA = S0 && S0.st[id]==='ghost' ? 0 : 1, ghostB = S1.st[id]==='ghost' ? 0 : 1;
    const op = lerp(S0 ? ghostA : ghostB, ghostB, e) * intro;
    const bx = boxes[id];
    bx.style.left = r1(x)+'px'; bx.style.opacity = r2(op);
    bx.style.background = `linear-gradient(${rgb(top)} 0%, ${rgb(bot)} 100%)`; bx.style.borderColor = rgb(br); bx.style.borderStyle='solid'; bx.style.borderWidth='2px';
    bx.style.boxShadow = `rgba(255,255,255,0.08) 0px 1px 0px inset, rgba(${h[0]},${h[1]},${h[2]},${h[3]}) 0px 0px 0px 4px`;
    const val = (e < 0.5 && S0) ? S0.vals[id] : S1.vals[id];
    if (L.bars) { const hv = +val, hh = hv*L.unit; bx.style.top = (L.base - hh)+'px'; bx.style.height = hh+'px'; bx.style.display = hv ? 'block':'none';
      const v = vlab[id]; v.textContent = val; v.style.left = r1(x)+'px'; v.style.color = rgb(tx); v.style.opacity = r2(intro); }
    else { bx.style.top = r1(L.boxTop - lift)+'px'; bx.style.color = rgb(tx); bx.textContent = val; }
    sig.push(r1(x), r1(lift), r2(op), top.join(), br.join(), h.join(), val);
  }
  for (const d of idx) d.style.opacity = r2(intro);
  if (L.bars) for (let i=0;i<n;i++) { const w0 = S0 ? (S0.water[i]||0) : 0, w1 = S1.water[i]||0; const lv = lerp(w0,w1,e); const slotId = S1.slots[i]; const hv = +S1.vals[slotId];
    const d = water[i]; d.style.top = (L.base - (hv+lv)*L.unit + 4)+'px'; d.style.height = Math.max(0, lv*L.unit - 8)+'px'; d.style.opacity = lv > 0.05 ? r2(intro) : 0; sig.push(r2(lv)); }
  const span = (f) => f ? [slotX(f[0]) - 12, slotX(f[1]) + L.w + 12] : null;
  const f0 = S0 && span(S0.frame), f1 = span(S1.frame);
  let fx = f1 || f0, fop = f1 ? (f0 ? 1 : e) : (f0 ? 1-e : 0);
  if (f0 && f1) fx = [lerp(f0[0],f1[0],e), lerp(f0[1],f1[1],e)];
  if (fx) { frame.style.left = r1(fx[0])+'px'; frame.style.width = r1(fx[1]-fx[0])+'px'; }
  frame.style.top = (L.bars ? L.base - 8 - 300 : L.boxTop - 12)+'px'; frame.style.height = (L.bars ? 316 : L.boxH + 24)+'px'; frame.style.opacity = r2(fop*intro);
  sig.push(fx ? fx.map(r1).join() : '', r2(fop));
  const b0 = S0 && S0.band, b1 = S1.band;
  const bs = b => b ? [slotX(b[0]), slotX(b[1]) + L.w] : null;
  let bb = bs(b1) || bs(b0), bop = b1 ? (b0 ? 1 : e) : (b0 ? 1-e : 0);
  if (b0 && b1) { const p = bs(b0), q = bs(b1); bb = [lerp(p[0],q[0],e), lerp(p[1],q[1],e)]; }
  if (bb) { band.style.left = r1(bb[0])+'px'; band.style.width = r1(bb[1]-bb[0])+'px'; bandLab.style.left = r1(bb[0])+'px'; bandLab.textContent = (b1||b0)[2] || ''; }
  band.style.opacity = bandLab.style.opacity = r2(bop*intro); sig.push(bb ? bb.map(r1).join() : '', r2(bop));
  for (const p of ptrNames) { const a = S0 ? S0.ptr[p] : undefined, b = S1.ptr[p]; const d = ptr[p];
    let x = b !== undefined ? slotX(b) : (a !== undefined ? slotX(a) : 0), o = b !== undefined ? (a !== undefined ? 1 : e) : (a !== undefined ? 1-e : 0);
    if (a !== undefined && b !== undefined) x = lerp(slotX(a), slotX(b), e);
    d.style.left = r1(x)+'px'; d.style.opacity = r2(o*intro); sig.push(r1(x), r2(o)); }
  const same = S0 && JSON.stringify(S0.eq) === JSON.stringify(S1.eq);
  const eqIn = S1.final ? T.FINAL_IN - 0.4 : T.EQ_IN, resIn = S1.final ? T.FINAL_IN + 0.2 : T.RES_IN;
  setEq(eqB, S1.eq, S1.final); setEq(eqA, S0 && S0.eq, S0 && S0.final);
  const outA = same ? 0 : sm(u / 0.6);
  eqA.style.opacity = S0 && !same ? r2(1 - outA) : 0; eqA.style.transform = `translateY(${r1(-14*outA)}px)`;
  const pin = same ? 1 : sm((u - eqIn) / 0.6), rin = same ? 1 : sm((u - resIn) / 0.5);
  eqB.p.style.opacity = r2(pin); eqB.r.style.opacity = r2(rin); eqB.style.transform = `translateY(${r1(14*(1-pin))}px)`;
  sig.push(r2(outA), r2(pin), r2(rin));
  TL.chips.forEach((c,i) => { const d = chips[i]; const o = c.step < k ? 1 : c.step === k ? sm((u - (S1.final ? T.FINAL_IN : T.CHIP_IN)) / 0.5) : 0;
    d.style.opacity = r2(o*intro); d.style.transform = `translateY(${r1(12*(1-o))}px)`; sig.push(r2(o)); });
  const cs = S0 && S0.caption === S1.caption;
  capA.textContent = S0 ? S0.caption : ''; capB.textContent = S1.caption;
  capB.style.color = S1.final ? '#CBE6FB' : '#F5F6F8'; capA.style.color = S0 && S0.final ? '#CBE6FB' : '#F5F6F8';
  const cOut = cs ? 0 : sm(u/0.6), cIn = cs ? 1 : sm((u - eqIn)/0.6);
  capA.style.opacity = S0 && !cs ? r2(1-cOut) : 0; capB.style.opacity = r2(cIn);
  capB.style.transform = `translateY(${r1(10*(1-cIn))}px)`; sig.push(r2(cOut), r2(cIn), k);
  return sig.join('|');
};
window.draw(TL.duration - T.FADE - 0.01);
})();
"""


def stage_div(v):
    L = layout(v)
    return f'<div id="stage" style="margin-top: 30px; position: relative; width: 920px; height: {L["height"]}px; flex: 0 0 auto"></div>'


def player_page(slide_html, tl, font_css):
    return ("<!doctype html><html><head><meta charset='utf-8'><style>" + font_css + "body{margin:0;background:#08090B}</style></head><body>"
            + slide_html + "<script>window.__TL=" + json.dumps(tl) + ";</script><script>" + PLAYER_JS + "</script></body></html>")
