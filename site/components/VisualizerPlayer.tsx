"use client";

// The step player. It knows nothing about any algorithm: it draws whatever
// steps a pattern in visualizer/patterns produces (schema in visualizer/schema.ts).
// Motion is CSS transforms only, driven by the difference between two steps.
// Layout is a fixed workbench: input on top, picture and controls on the left,
// pseudocode on the right scrolling inside its own box, so one screen holds it all.
import { use, useEffect, useId, useMemo, useRef, useState, type CSSProperties, type KeyboardEvent } from "react";
import { loadPattern } from "@/visualizer/loaders.ts";
import { checkLimits, traceOf, type Field, type Input, type Pattern, type StackItem } from "@/visualizer/schema.ts";

const SPEEDS = [0.5, 1, 2];
const STEP_MS = 1600;
const LINE_PX = 22; // one pseudocode line (see .vz-code pre.shiki)

type Texts = Record<string, string>;
type Problem = { field?: string; msg: string };
type Props = { patternId: string; codeHtml: string; locked?: boolean };

const textsOf = (input: Input): Texts =>
  Object.fromEntries(Object.entries(input).map(([k, v]) => [k, Array.isArray(v) ? v.join(", ") : String(v)]));

function parseField(f: Field, text: string): number | number[] | Problem {
  const parts = text.split(/[\s,]+/).filter(Boolean);
  for (const t of parts) {
    if (!/^[-+]?\d{1,9}$/.test(t)) return { field: f.name, msg: `${f.label}: "${t.slice(0, 12)}" is not a whole number.` };
  }
  const nums = parts.map(Number);
  if (f.kind === "int") {
    if (nums.length !== 1) return { field: f.name, msg: `${f.label} needs exactly one number.` };
    return nums[0];
  }
  return nums;
}

function parseInput(p: Pattern, texts: Texts): Input | Problem {
  const input: Input = {};
  for (const f of p.fields) {
    const v = parseField(f, texts[f.name] ?? "");
    if (typeof v === "object" && !Array.isArray(v)) return v;
    input[f.name] = v;
    const bad = checkLimits([f], input);
    if (bad) return { field: f.name, msg: bad };
  }
  const bad = p.validate(input);
  return bad ? { msg: bad } : input;
}

const vars = (o: Record<string, string | number>) => o as CSSProperties;

// Each pattern is its own chunk, fetched the first time a player asks for it.
export default function VisualizerPlayer(props: Props) {
  return <Workbench {...props} p={use(loadPattern(props.patternId))} />;
}

function Workbench({ p, codeHtml, locked }: Props & { p: Pattern }) {
  const uid = useId();
  const codeRef = useRef<HTMLDivElement>(null);
  const [texts, setTexts] = useState<Texts>(() => textsOf(p.example));
  const [input, setInput] = useState<Input>(p.example);
  const [problem, setProblem] = useState<Problem | null>(null);
  const [pos, setPos] = useState({ i: 0, prev: 0 });
  const [wantPlay, setWantPlay] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [panel, setPanel] = useState<"code" | "input">("code"); // phones show one at a time

  const trace = useMemo(() => traceOf(p, input), [p, input]);
  const last = trace.steps.length - 1;
  const step = trace.steps[Math.min(pos.i, last)];
  const before = trace.steps[Math.min(pos.prev, last)];
  const playing = wantPlay && pos.i < last;
  const n = Math.max(1, step.cells.length);
  // What the stage needs room for is decided once per trace, so stepping never changes the layout.
  const shape = useMemo(
    () => ({
      // Pointers alternate below and above the cells, in the order they first appear, and keep their side.
      top: [...new Set(trace.steps.flatMap((s) => s.pointers.map((q) => q.id)))].filter((_, k) => k % 2 === 1),
      stack: trace.steps.some((s) => s.stack),
      window: trace.steps.some((s) => s.window),
      vars: trace.steps[0].vars?.map((v) => v.name) ?? [],
    }),
    [trace],
  );

  useEffect(() => {
    if (!playing) return;
    const t = setInterval(() => setPos((c) => (c.i >= last ? c : { i: c.i + 1, prev: c.i })), STEP_MS / speed);
    return () => clearInterval(t);
  }, [playing, speed, last]);

  // Long pseudocode scrolls inside its box; keep the running line in the middle of it.
  useEffect(() => {
    const el = codeRef.current;
    if (el && el.scrollHeight > el.clientHeight + 1) el.scrollTop = 12 + step.line * LINE_PX + LINE_PX / 2 - el.clientHeight / 2;
  }, [step.line]);

  const go = (to: number) => {
    setWantPlay(false);
    setPos((c) => {
      const i = Math.max(0, Math.min(last, to));
      return i === c.i ? c : { i, prev: c.i };
    });
  };
  const togglePlay = () => {
    if (playing) return setWantPlay(false);
    if (pos.i >= last) setPos({ i: 0, prev: 0 });
    setWantPlay(true);
  };
  const load = (next: Input) => {
    setInput(next);
    setTexts(textsOf(next));
    setProblem(null);
    setWantPlay(false);
    setPos({ i: 0, prev: 0 });
  };
  const submit = () => {
    const r = parseInput(p, texts);
    if ("msg" in r && typeof r.msg === "string") return setProblem(r as Problem);
    load(r as Input);
    setWantPlay(true); // Run plays the reader's input from the first step
  };

  const onKey = (e: KeyboardEvent<HTMLDivElement>) => {
    const tag = (e.target as HTMLElement).tagName;
    if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA" || e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.key === " " && tag === "BUTTON") return;
    if (e.key === " " || e.key === "k") togglePlay();
    else if (e.key === "ArrowRight") go(pos.i + 1);
    else if (e.key === "ArrowLeft") go(pos.i - 1);
    else if (e.key === "Home") go(0);
    else if (e.key === "End") go(last);
    else return;
    e.preventDefault();
  };

  const stack = step.stack ?? [];
  const leaving: { item: StackItem; at: number }[] = [];
  if (pos.prev !== pos.i) {
    (before.stack ?? []).forEach((item, at) => {
      if (!stack.some((s) => s.id === item.id)) leaving.push({ item, at });
    });
  }
  const win = step.window;
  const winLen = win ? win.hi - win.lo + 1 : 0;
  const done = pos.i >= last;

  return (
    <div
      className="vz"
      role="group"
      aria-label={`${p.title} visualizer`}
      tabIndex={0}
      onKeyDown={onKey}
      data-panel={panel}
      style={vars({ "--n": n, "--vz-dur": `${Math.round(Math.min(520, 520 / speed))}ms` })}
    >
      <div className="vz-inputs" id={`${uid}-input`}>
        {locked ? (
          <p className="vz-lock">This is a preview on the post&apos;s example. Running your own input is part of the full version.</p>
        ) : (
          <form
            className="vz-form"
            noValidate
            onSubmit={(e) => {
              e.preventDefault();
              submit();
            }}
          >
            {p.fields.map((f) => (
              <label key={f.name} className={`vz-field vz-field-${f.kind}`}>
                <span>
                  {f.label}
                  <small>{f.kind === "ints" ? ` ${f.minLen ?? 0} to ${f.maxLen} numbers, ${f.min} to ${f.max}` : ` ${f.min} to ${f.max}`}</small>
                </span>
                <input
                  type="text"
                  inputMode="text"
                  autoComplete="off"
                  spellCheck={false}
                  maxLength={120}
                  value={texts[f.name] ?? ""}
                  onChange={(e) => setTexts({ ...texts, [f.name]: e.target.value })}
                  aria-invalid={problem && (!problem.field || problem.field === f.name) ? true : undefined}
                  aria-describedby={problem ? `${uid}-err` : undefined}
                />
              </label>
            ))}
            <div className="vz-actions">
              <button type="submit" className="vz-btn vz-text-btn vz-go">Run</button>
              <button type="button" className="vz-btn vz-text-btn" onClick={() => load(p.random(Math.random))}>Random</button>
              <button type="button" className="vz-btn vz-text-btn" onClick={() => load(p.example)}>Reset</button>
            </div>
          </form>
        )}
        <div className="vz-status">
          <p className="vz-error" id={`${uid}-err`} role="alert">
            {problem?.msg}
          </p>
          {!problem && <p className="vz-hint">{p.problem}</p>}
        </div>
      </div>

      <div className="vz-left">
        <div className="vz-stage" aria-hidden="true">
          <div className="vz-grid">
            {shape.top.length > 0 && (
              <div className="vz-ptrs vz-ptrs-top">
                {step.pointers.map((ptr) =>
                  shape.top.includes(ptr.id) ? (
                    <div key={ptr.id} className="vz-ptr" style={vars({ "--at": ptr.at })}>
                      <span>{ptr.label}</span>
                      <i />
                    </div>
                  ) : null,
                )}
              </div>
            )}
            <div className="vz-cells">
              {shape.window && (
                <div className={`vz-win${win && winLen > 0 ? "" : " vz-win-empty"}`} style={vars({ "--lo": win?.lo ?? 0, "--len": Math.max(winLen, 0) })} />
              )}
              {step.cells.map((c, i) => (
                <div key={i} className={`vz-cell vz-${c.state}`}>
                  <span>{c.v}</span>
                </div>
              ))}
            </div>
            <div className="vz-idx">
              {step.cells.map((_, i) => (
                <span key={i}>{i}</span>
              ))}
            </div>
            <div className="vz-ptrs vz-ptrs-bottom">
              {step.pointers.map((ptr) =>
                !shape.top.includes(ptr.id) ? (
                  <div key={ptr.id} className="vz-ptr" style={vars({ "--at": ptr.at })}>
                    <i />
                    <span>{ptr.label}</span>
                  </div>
                ) : null,
              )}
            </div>
            {shape.stack && (
              <>
                <div className="vz-stack-label">Stack · top on the right</div>
                <div className="vz-stack">
                  {stack.map((item, at) => (
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
            )}
          </div>
          {shape.vars.length > 0 && (
            <div className="vz-vars">
              {shape.vars.map((name) => {
                const v = step.vars?.find((x) => x.name === name)?.value ?? "";
                return (
                  <div key={name} className="vz-var">
                    <span>{name}</span>
                    <b>{v === "" ? "–" : v}</b>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="vz-say">
          <p aria-live="polite" aria-atomic="true">
            <span className="vz-visually-hidden">{`Step ${pos.i + 1} of ${last + 1}. `}</span>
            {step.say}
            {done && <span className="vz-visually-hidden">{` Answer: ${p.answerText(trace.answer)}.`}</span>}
          </p>
          <p className={`vz-answer${done ? " vz-answer-on" : ""}`} aria-hidden="true">
            {done ? p.answerText(trace.answer) : " "}
          </p>
        </div>

        <div className="vz-controls">
          <input
            className="vz-scrub"
            type="range"
            min={0}
            max={last}
            step={1}
            value={pos.i}
            onChange={(e) => go(Number(e.target.value))}
            aria-label="Step"
            aria-valuetext={`Step ${pos.i + 1} of ${last + 1}`}
          />
          <div className="vz-buttons">
            <button type="button" className="vz-btn" onClick={() => go(0)} disabled={pos.i === 0} aria-label="Back to the start">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 5v14M19 5l-9 7 9 7z" /></svg>
            </button>
            <button type="button" className="vz-btn" onClick={() => go(pos.i - 1)} disabled={pos.i === 0} aria-label="Step back">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-8 7 8 7z" /></svg>
            </button>
            <button type="button" className="vz-btn vz-play" onClick={togglePlay} aria-label={playing ? "Pause" : done ? "Play again" : "Play"} title="Space plays, ← → step, Home and End jump">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                {playing ? <path d="M8 5v14M16 5v14" /> : <path d="M8 5l11 7-11 7z" />}
              </svg>
            </button>
            <button type="button" className="vz-btn" onClick={() => go(pos.i + 1)} disabled={done} aria-label="Step forward">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l8 7-8 7z" /></svg>
            </button>
            <span className="vz-count" aria-hidden="true">
              {pos.i + 1} / {last + 1}
            </span>
            <label className="vz-speed">
              <span className="vz-visually-hidden">Speed</span>
              <select value={speed} onChange={(e) => setSpeed(Number(e.target.value))}>
                {SPEEDS.map((s) => (
                  <option key={s} value={s}>
                    {s}×
                  </option>
                ))}
              </select>
            </label>
          </div>
        </div>
      </div>

      <div className="vz-tabs" role="tablist" aria-label="Show">
        <button type="button" role="tab" className="vz-tab" aria-selected={panel === "code"} aria-controls={`${uid}-code`} onClick={() => setPanel("code")}>
          Pseudocode
        </button>
        <button type="button" role="tab" className="vz-tab" aria-selected={panel === "input"} aria-controls={`${uid}-input`} onClick={() => setPanel("input")}>
          Your input
        </button>
      </div>

      <div className="vz-code-slot" id={`${uid}-code`}>
        <div className="vz-code pseudo-block">
          <div className="pseudo-head">{"Pseudocode  ·  any language"}</div>
          <div className="vz-code-scroll" ref={codeRef}>
            <div className="vz-code-body" style={vars({ "--line": step.line })}>
              <div className="vz-code-mark" />
              <div dangerouslySetInnerHTML={{ __html: codeHtml }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
