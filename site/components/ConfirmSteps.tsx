// The three cells from the confirmation email, drawn like the visualizer's array:
// index numbers underneath and a pointer on the cell the reader is at.
const CELLS = ["sign up", "confirm", "learn"];

export function ConfirmSteps({ at }: { at: number }) {
  return (
    <div className="steps" role="img" aria-label={`Step ${at + 1} of 3: ${CELLS[at]}`}>
      {CELLS.map((name, i) => (
        <div key={name} className="steps-col">
          <div className={i < at ? "steps-cell is-done" : i === at ? "steps-cell is-here" : "steps-cell is-ahead"}>
            {i < at && <span aria-hidden="true">✓ </span>}
            {name}
          </div>
          <div className="steps-index">{i}</div>
          <div className="steps-pointer" aria-hidden="true">
            {i === at ? "▲ you" : ""}
          </div>
        </div>
      ))}
    </div>
  );
}
