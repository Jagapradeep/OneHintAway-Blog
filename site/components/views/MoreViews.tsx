// The less common views (schema v2): map, bars and grid. One chunk, loaded only
// by patterns that use one of them. Rows of the player's .vz-grid.
import type { BarsView as BarsData, GridView as GridData, MapEntry, MapView as MapData } from "@/visualizer/schema.ts";
import { vars } from "./vars.ts";

const Label = ({ text }: { text?: string }) => (text ? <div className="vz-stack-label">{text}</div> : null);

/** `all` is every entry the map holds at some step of the trace: each keeps its
 *  place from the start, hidden until the map really has it, so nothing jumps. */
export function MapView({ view, all }: { view: MapData; all: MapEntry[] }) {
  return (
    <>
      <Label text={view.label ?? "Map"} />
      <div className="vz-map">
        {all.map((slot) => {
          const e = view.entries.find((x) => x.id === slot.id);
          return (
            <div key={slot.id} className={e ? `vz-entry vz-e-${e.state}` : "vz-entry vz-entry-off"}>
              <b>{(e ?? slot).k}</b>
              <span>{(e ?? slot).v}</span>
            </div>
          );
        })}
      </div>
    </>
  );
}

export function BarsView({ view }: { view: BarsData }) {
  const max = Math.max(1, ...view.bars.map((b) => b.h));
  return (
    <>
      <Label text={view.label} />
      <div className="vz-bars" style={vars({ "--max": max })}>
        {view.bars.map((b) => (
          <div key={b.id} className={`vz-bar vz-b-${b.state}`} style={vars({ "--h": b.h, "--w": b.water })}>
            <i className="vz-water" />
            <i className="vz-wall" />
          </div>
        ))}
      </div>
      <div className="vz-idx">
        {view.bars.map((b) => (
          <span key={b.id}>{b.h}</span>
        ))}
      </div>
      <div className="vz-ptrs vz-ptrs-bottom">
        {view.pointers.map((ptr) => (
          <div key={ptr.id} className="vz-ptr" style={vars({ "--at": ptr.at })}>
            <i />
            <span>{ptr.label}</span>
          </div>
        ))}
      </div>
    </>
  );
}

export function GridView({ view }: { view: GridData }) {
  return (
    <>
      <Label text={view.label} />
      {view.rows.map((row, y) => (
        <div key={y} className="vz-cells">
          {row.map((c, x) => (
            <div key={c.id} className={`vz-cell vz-${c.state}`} style={vars({ "--at": x })}>
              <span>{c.v}</span>
            </div>
          ))}
        </div>
      ))}
    </>
  );
}
