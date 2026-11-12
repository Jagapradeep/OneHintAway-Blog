"""Writes the website visualizer's test fixtures from post-kit/viz/<pattern>/ref.py.

    python post-kit/tools/viz_fixtures.py            # every pattern
    python post-kit/tools/viz_fixtures.py two-pointers

Each fixture (site/visualizer/fixtures/<pattern>.json) holds the example's full
step trace from viz_steps() and the brute-force answer for every test input.
`npm run build` in site/ checks the TypeScript engine against them, so the
cloud build never needs Python. Re-run this whenever a ref.py changes.
"""
import importlib.util
import json
import sys
from pathlib import Path

SCHEMA = 1
ROOT = Path(__file__).resolve().parents[2]
VIZ = ROOT / "post-kit" / "viz"
OUT = ROOT / "site" / "visualizer" / "fixtures"


def load(path):
    spec = importlib.util.spec_from_file_location("viz_ref_" + path.parent.name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def trace(ref, inp):
    return {"schema": SCHEMA, "pattern": ref.PATTERN, "input": inp, "pseudocode": ref.PSEUDOCODE,
            "steps": ref.viz_steps(inp), "answer": ref.solve(inp)}


def build(folder):
    ref = load(folder / "ref.py")
    if ref.PATTERN != folder.name:
        sys.exit(f"{folder.name}: PATTERN is '{ref.PATTERN}', the folder name must match")
    inputs = ref.test_inputs()
    if len(inputs) < 1000:
        sys.exit(f"{folder.name}: only {len(inputs)} test inputs (at least 1,000 needed)")
    same = getattr(ref, "same", lambda inp, got, want: got == want)
    cases = []
    for inp in inputs:
        want = ref.brute(inp)
        got = ref.solve(inp)
        if not same(inp, got, want):
            sys.exit(f"{folder.name}: solve() disagrees with brute() on {json.dumps(inp)[:200]}: {got} vs {want}")
        cases.append({"in": inp, "out": want})
    data = {"schema": SCHEMA, "pattern": ref.PATTERN, "example": trace(ref, ref.EXAMPLE), "cases": cases}
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{ref.PATTERN}.json"
    path.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{ref.PATTERN}: {len(cases)} cases, {len(data['example']['steps'])} example steps -> {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")


def main():
    wanted = sys.argv[1:]
    folders = sorted(p for p in VIZ.iterdir() if (p / "ref.py").exists() and (not wanted or p.name in wanted))
    if not folders:
        sys.exit("no post-kit/viz/<pattern>/ref.py found")
    for folder in folders:
        build(folder)


if __name__ == "__main__":
    main()
