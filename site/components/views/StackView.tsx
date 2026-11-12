// Draws one stack view (schema v2): bottom on the left, top on the right.
// Rows of the player's .vz-grid.
import type { StackView as StackViewData } from "@/visualizer/schema.ts";
import { vars } from "./vars.ts";

interface Props {
  view: StackViewData;
  /** The same view on the step the reader just left, so popped items can animate out. */
  before?: StackViewData;
}

export function StackView({ view, before }: Props) {
  const leaving = (before?.items ?? [])
    .map((item, at) => ({ item, at }))
    .filter(({ item }) => !view.items.some((s) => s.id === item.id));
  return (
    <>
      <div className="vz-stack-label">{view.label ?? "Stack"} · top on the right</div>
      <div className="vz-stack">
        {view.items.map((item, at) => (
          <div key={item.id} className="vz-item" style={vars({ "--at": at })}>
            <span>{item.v}</span>
          </div>
        ))}
        {leaving.map(({ item, at }) => (
          <div key={item.id} className="vz-item vz-item-out" style={vars({ "--at": at })}>
            <span>{item.v}</span>
          </div>
        ))}
      </div>
    </>
  );
}
