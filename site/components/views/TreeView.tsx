// Draws one tree view (schema v2). Loaded in its own chunk, only by patterns
// that have a tree. A node's column is its in-order rank and its row is its
// depth, so a binary-search decision tree lines up with the array's cells.
import type { TreeNode, TreeView as TreeViewData } from "@/visualizer/schema.ts";
import { vars } from "./vars.ts";

export default function TreeView({ view }: { view: TreeViewData }) {
  const kids = new Map<string, TreeNode[]>();
  let root: TreeNode | undefined;
  for (const nd of view.nodes) {
    if (nd.parent === undefined) root = nd;
    else kids.set(nd.parent, [...(kids.get(nd.parent) ?? []), nd]);
  }
  const at = new Map<string, { x: number; y: number }>();
  let rows = 0;
  const place = (nd: TreeNode, y: number) => {
    const below = kids.get(nd.id) ?? [];
    for (const k of below) if (k.side === "left") place(k, y + 1);
    at.set(nd.id, { x: at.size, y });
    for (const k of below) if (k.side !== "left") place(k, y + 1);
    rows = Math.max(rows, y + 1);
  };
  if (root) place(root, 0);
  const n = Math.max(1, view.nodes.length);
  return (
    <>
      {view.label && <div className="vz-stack-label">{view.label}</div>}
      <div className="vz-tree" style={vars({ "--n": n, "--rows": rows })}>
        <svg className="vz-edges" viewBox={`0 0 ${n} ${Math.max(1, rows)}`} preserveAspectRatio="none">
          {view.nodes.map((nd) => {
            const a = at.get(nd.id);
            const b = nd.parent === undefined ? undefined : at.get(nd.parent);
            return a && b ? (
              <line key={nd.id} className={nd.state === "dim" ? "vz-edge-off" : nd.state === "plain" ? undefined : "vz-edge-on"} x1={b.x + 0.5} y1={b.y + 0.5} x2={a.x + 0.5} y2={a.y + 0.5} />
            ) : null;
          })}
        </svg>
        {view.nodes.map((nd) => {
          const a = at.get(nd.id) ?? { x: 0, y: 0 };
          return (
            <div key={nd.id} className={`vz-node vz-${nd.state}`} style={vars({ "--at": a.x, "--row": a.y })}>
              <span>{nd.v}</span>
            </div>
          );
        })}
      </div>
    </>
  );
}
