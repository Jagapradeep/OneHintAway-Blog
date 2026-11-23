// Draws one tree view (schema v2). Loaded in its own chunk, only by patterns
// that have a tree. A node's column is its in-order rank and its row is its
// depth, so a binary-search decision tree lines up with the array's cells.
// A tree without sides (a decision tree of choices) is drawn compact instead.
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
  // No sides: compact layout. Leaves take one column each, a parent sits over the middle of its children.
  const compact = !view.nodes.some((nd) => nd.side !== undefined);
  let leaves = 0;
  const tidy = (nd: TreeNode, y: number): number => {
    const below = kids.get(nd.id) ?? [];
    const xs = below.map((k) => tidy(k, y + 1));
    const x = xs.length ? (xs[0] + xs[xs.length - 1]) / 2 : leaves++;
    at.set(nd.id, { x, y });
    rows = Math.max(rows, y + 1);
    return x;
  };
  if (root) {
    if (compact) tidy(root, 0);
    else place(root, 0);
  }
  const n = Math.max(1, compact ? leaves : view.nodes.length);
  // One text size for the whole tree, set by its longest label, so every node matches.
  const len = Math.max(1, ...view.nodes.map((nd) => String(nd.v).length));
  return (
    <>
      {view.label && <div className="vz-stack-label">{view.label}</div>}
      <div className="vz-tree" style={vars({ "--n": n, "--rows": rows, "--len": len })}>
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
