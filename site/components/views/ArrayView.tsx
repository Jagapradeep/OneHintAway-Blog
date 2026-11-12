// Draws one array view (schema v2): pointers above, the cells with an optional
// window frame, the index row, pointers below. Rows of the player's .vz-grid.
import type { ArrayView as ArrayViewData } from "@/visualizer/schema.ts";
import { vars } from "./vars.ts";

interface Props {
  view: ArrayViewData;
  /** Ids of the pointers drawn above the cells; the rest go below. Fixed per trace. */
  top: string[];
  /** Whether any step of the trace has a window, so the frame can animate in and out. */
  hasWindow: boolean;
}

export function ArrayView({ view, top, hasWindow }: Props) {
  const win = view.window;
  const winLen = win ? win.hi - win.lo + 1 : 0;
  // Drawn in id order, whatever their positions: a cell that moves keeps its
  // element and its place in the DOM, so CSS can slide it to the new position.
  const cells = view.cells.map((c, at) => ({ c, at })).sort((a, b) => (a.c.id < b.c.id ? -1 : a.c.id > b.c.id ? 1 : 0));
  return (
    <>
      {top.length > 0 && (
        <div className="vz-ptrs vz-ptrs-top">
          {view.pointers.map((ptr) =>
            top.includes(ptr.id) ? (
              <div key={ptr.id} className="vz-ptr" style={vars({ "--at": ptr.at })}>
                <span>{ptr.label}</span>
                <i />
              </div>
            ) : null,
          )}
        </div>
      )}
      <div className="vz-cells">
        {hasWindow && (
          <div className={`vz-win${win && winLen > 0 ? "" : " vz-win-empty"}`} style={vars({ "--lo": win?.lo ?? 0, "--len": Math.max(winLen, 0) })} />
        )}
        {cells.map(({ c, at }) => (
          <div key={c.id} className={`vz-cell vz-${c.state}`} style={vars({ "--at": at })}>
            <span>{c.v}</span>
          </div>
        ))}
      </div>
      <div className="vz-idx">
        {view.cells.map((_, i) => (
          <span key={i}>{i}</span>
        ))}
      </div>
      <div className="vz-ptrs vz-ptrs-bottom">
        {view.pointers.map((ptr) =>
          !top.includes(ptr.id) ? (
            <div key={ptr.id} className="vz-ptr" style={vars({ "--at": ptr.at })}>
              <i />
              <span>{ptr.label}</span>
            </div>
          ) : null,
        )}
      </div>
    </>
  );
}
