// The three steps from the confirmation email: what is done, where the reader is, what is next.
const STEPS = ["Signed up", "Confirm email", "Start learning"];

export function ConfirmSteps({ at }: { at: number }) {
  return (
    <div className="confirm-steps" role="img" aria-label={`Step ${at + 1} of 3: ${STEPS[at]}`}>
      {STEPS.map((name, i) => (
        <div key={name} className="confirm-steps-col">
          <div className={i < at ? "confirm-steps-cell is-done" : i === at ? "confirm-steps-cell is-here" : "confirm-steps-cell is-ahead"}>
            {i < at && <span aria-hidden="true">✓ </span>}
            {name}
          </div>
          <div className={i === at ? "confirm-steps-status is-here" : "confirm-steps-status"} aria-hidden="true">
            {i < at ? "done" : i === at ? "▲ you are here" : "next"}
          </div>
        </div>
      ))}
    </div>
  );
}
