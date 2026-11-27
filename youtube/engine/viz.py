"""Cue-driven array pictures for the final videos: cells with ids that slide into new orders,
pointer labels that glide, arcs that draw in, colours that blend. Deterministic: draw(t) only."""
import re

def cue(scene, spec):
    """'L2+0.4' -> seconds from the scene start."""
    if isinstance(spec, (int, float)):
        return float(spec)
    m = re.match(r"^([A-Za-z0-9]+)([+-][0-9.]+)?$", spec)
    return scene["cues"][m.group(1)] + (float(m.group(2)) if m.group(2) else 0.0)

def arr(scene, vid, values, x, y, cell=120, gap=16, states=(), ptr_size=26, arc_h=1.0):
    """Attach an array picture to a scene. states: list of (cue, {order, st, ptr, arcs, split, hide})."""
    out = []
    for spec, s in states:
        d = dict(s); d["t"] = round(cue(scene, spec), 3)
        out.append(d)
    scene.setdefault("viz", []).append({"id": vid, "values": values, "x": x, "y": y, "cell": cell, "gap": gap,
                                        "states": out, "ps": ptr_size, "ah": arc_h})

VIZ_JS = r"""
(function(){
const PAL = {plain:[[22,24,29],[61,66,76],[230,232,236]], gold:[[58,46,21],[221,178,90],[255,227,160]],
  steel:[[28,48,68],[127,176,218],[203,230,251]], dim:[[17,18,21],[35,38,44],[74,79,89]], red:[[58,26,24],[229,115,107],[255,194,188]]};
const ARC = {gold:'#F4CF6E', steel:'#7FB0DA', red:'#E5736B', dim:'#3A3F49'};
const sm = x => { x = Math.min(1, Math.max(0, x)); return x*x*(3-2*x); };
const mix = (a, b, e) => a.map((v, i) => Math.round(v + (b[i]-v)*e));
const rgb = c => `rgb(${c[0]},${c[1]},${c[2]})`;
const NS = 'http://www.w3.org/2000/svg';
const V = [];
for (const s of window.__D.scenes) for (const z of (s.viz || [])) {
  const host = document.getElementById('sc_' + s.id); if (!host) continue;
  const n = z.values.length, el = document.createElement('div');
  el.style.cssText = `position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none`;
  const svg = document.createElementNS(NS, 'svg'); svg.setAttribute('width', '100%'); svg.setAttribute('height', '100%');
  svg.style.cssText = 'position:absolute;left:0;top:0;overflow:visible'; el.appendChild(svg);
  const cells = z.values.map(v => { const c = document.createElement('div');
    c.style.cssText = `position:absolute;width:${z.cell}px;height:${z.cell}px;border-radius:${Math.round(z.cell*0.16)}px;box-sizing:border-box;border:${z.cell>90?3:2}px solid;display:flex;align-items:center;justify-content:center;font-family:'Geist Mono',monospace;font-weight:600;font-size:${Math.round(z.cell*0.42)}px;box-shadow:0 10px 24px rgba(0,0,0,.35)`;
    c.textContent = v; el.appendChild(c); return c; });
  host.appendChild(el);
  V.push({s, z, el, svg, cells, ptrs: {}, arcs: {}});
}
function slotX(z, st, k){ const sp = st.split || []; const extra = sp.filter(p => p <= k).length * z.cell * 0.55;
  const n = z.values.length, tot = n*z.cell + (n-1)*z.gap + sp.length*z.cell*0.55; return z.x - tot/2 + k*(z.cell+z.gap) + extra; }
function pos(z, st, id){ const order = st.order || z.values.map((_, i) => i); return slotX(z, st, order.indexOf(id)); }
window.drawViz = function(t){
  for (const v of V) {
    const local = t - v.s.t0, S = v.z.states; let k = -1;
    for (let i = 0; i < S.length; i++) if (local >= S[i].t) k = i;
    const cur = S[Math.max(k, 0)], prev = S[Math.max(k-1, 0)], e = k < 0 ? 1 : sm((local - cur.t) / (cur.dur || 0.45)), z = v.z;
    v.el.style.opacity = k < 0 ? 0 : 1;
    v.cells.forEach((c, id) => {
      const x = prev === cur ? pos(z, cur, id) : pos(z, prev, id) + (pos(z, cur, id) - pos(z, prev, id)) * e;
      const lift = (cur.up || []).includes(id) ? -z.cell*0.35*e : ((prev.up || []).includes(id) ? -z.cell*0.35*(1-e) : 0);
      c.style.left = x + 'px'; c.style.top = (z.y + lift) + 'px';
      const a = PAL[(prev.st || {})[id] || 'plain'], b = PAL[(cur.st || {})[id] || 'plain'];
      c.style.background = rgb(mix(a[0], b[0], e)); c.style.borderColor = rgb(mix(a[1], b[1], e)); c.style.color = rgb(mix(a[2], b[2], e));
      const hid0 = (prev.hide || []).includes(id), hid1 = (cur.hide || []).includes(id);
      c.style.opacity = hid0 && hid1 ? 0 : hid1 ? 1 - e : hid0 ? e : 1;
    });
    // pointers (by slot), stacked when they share a slot
    const P = cur.ptr || {}, P0 = prev.ptr || {};
    const names = new Set([...Object.keys(P), ...Object.keys(P0)]);
    for (const nm of names) {
      let d = v.ptrs[nm]; if (!d) { d = document.createElement('div'); d.textContent = nm;
        d.style.cssText = `position:absolute;font-family:'Geist Mono',monospace;font-weight:600;font-size:${v.z.ps}px;letter-spacing:2px;color:#CBE6FB;text-align:center;width:${v.z.cell*1.6}px;white-space:nowrap`;
        v.el.appendChild(d); v.ptrs[nm] = d; }
      const slot1 = P[nm], slot0 = P0[nm] !== undefined ? P0[nm] : slot1;
      const sx = s => slotX(z, cur, s) + z.cell/2 - z.cell*0.8;
      const x = slot1 === undefined ? sx(slot0) : sx(slot0) + (sx(slot1) - sx(slot0)) * e;
      const row = Object.keys(P).filter(o => P[o] === slot1).indexOf(nm);
      d.style.left = x + 'px'; d.style.top = (z.y + z.cell + 16 + Math.max(0,row) * (v.z.ps + 8)) + 'px';
      d.style.opacity = slot1 === undefined ? 1 - e : (P0[nm] === undefined ? e : 1);
      d.style.color = (cur.pcol || {})[nm] || '#CBE6FB';
    }
    // arcs above the cells, drawing in when new
    const A = cur.arcs || [], A0 = new Set((prev === cur ? [] : (prev.arcs || [])).map(a => a.join(',')));
    const keep = new Set();
    for (const a of A) {
      const key = a.join(','); keep.add(key);
      let p = v.arcs[key]; if (!p) { p = document.createElementNS(NS, 'path'); p.setAttribute('fill', 'none'); p.setAttribute('stroke-linecap', 'round'); v.svg.appendChild(p); v.arcs[key] = p; }
      const order = cur.order || z.values.map((_, i) => i);
      const x1 = slotX(z, cur, a[0]) + z.cell/2, x2 = slotX(z, cur, a[1]) + z.cell/2, y0 = z.y - 10;
      const h = Math.min(z.cell*2.2, 40 + Math.abs(x2-x1)*0.32) * v.z.ah;
      p.setAttribute('d', `M ${x1} ${y0} Q ${(x1+x2)/2} ${y0 - h*2} ${x2} ${y0}`);
      p.setAttribute('stroke', ARC[a[2] || 'gold']); p.setAttribute('stroke-width', a[3] || 5);
      const L = p.getTotalLength(); p.setAttribute('stroke-dasharray', L);
      const fresh = !A0.has(key) && a[4] !== 'full'; p.setAttribute('stroke-dashoffset', fresh ? L * (1 - e) : 0);
      p.style.opacity = 1;
    }
    for (const key in v.arcs) if (!keep.has(key)) v.arcs[key].style.opacity = 0;
  }
};
})();
"""
