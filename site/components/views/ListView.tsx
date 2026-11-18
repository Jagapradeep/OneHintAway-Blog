// Draws one linked-list view (schema v2). Loaded in its own chunk, only by
// patterns that have a list. Nodes sit in fixed columns and never move; the
// arrows between them appear, flip or loop back as `next` changes. The column
// after the last node is "none", where a pointer stands when it is none.
// Each pointer has its own row under the nodes, so two on one node never overlap.
import type { ListView as ListData } from "@/visualizer/schema.ts";
import { vars } from "./vars.ts";

export default function ListView({ view, rows }: { view: ListData; rows: string[] }) {
  const n = view.nodes.length;
  const col = new Map(view.nodes.map((nd, i) => [nd.id, i]));
  const colOf = (at: string | null) => (at === null ? n : (col.get(at) ?? n));
  const used = new Set(view.pointers.map((p) => colOf(p.at)));
  // Arrows to a neighbour are straight; any other arrow (a loop back) is an arc above the row.
  const arcs = view.nodes.flatMap((nd, i) => {
    if (nd.next === null) return [];
    const j = col.get(nd.next) ?? i;
    return Math.abs(i - j) === 1 ? [] : [{ key: `${nd.id}>${nd.next}`, i, j }];
  });
  return (
    <>
      {view.label && <div className="vz-stack-label">{view.label}</div>}
      <div className="vz-lrow">
        {view.nodes.slice(0, -1).map((nd, g) => (
          <span key={`f${nd.id}`} className={`vz-link${nd.next === view.nodes[g + 1].id ? "" : " vz-link-off"}`} style={vars({ "--at": g })} />
        ))}
        {view.nodes.slice(1).map((nd, k) => (
          <span key={`b${nd.id}`} className={`vz-link vz-link-back${nd.next === view.nodes[k].id ? "" : " vz-link-off"}`} style={vars({ "--at": k })} />
        ))}
        {arcs.map((a) => (
          <span
            key={a.key}
            className={`vz-arc${a.j < a.i ? " vz-arc-left" : ""}`}
            style={vars({ "--from": Math.min(a.i, a.j), "--span": Math.max(Math.abs(a.i - a.j), 0.4) })}
          />
        ))}
        {view.nodes.map((nd, i) => (
          <div key={nd.id} className={`vz-cell vz-${nd.state}`} style={vars({ "--at": i })}>
            <span>{nd.v}</span>
          </div>
        ))}
        <div className="vz-cell vz-lnone" style={vars({ "--at": n })}>
          <span>none</span>
        </div>
      </div>
      <div className="vz-carets">
        {view.nodes.map((nd, i) => (
          <i key={nd.id} className={used.has(i) ? undefined : "vz-caret-off"} style={vars({ "--at": i })} />
        ))}
        <i className={used.has(n) ? undefined : "vz-caret-off"} style={vars({ "--at": n })} />
      </div>
      {rows.map((id) => {
        const p = view.pointers.find((q) => q.id === id);
        return (
          <div key={id} className="vz-lptr">
            {p && (
              <div className="vz-ptr" style={vars({ "--at": colOf(p.at) })}>
                <span>{p.label}</span>
              </div>
            )}
          </div>
        );
      })}
    </>
  );
}
