"""Code tests in four languages, the blog MDX, the caption and the alt text.
Contract v1.2 (dsa-post section 10). Every count in "How it was tested" is the
count that really ran."""
import json
import re
import shutil
import subprocess
from pathlib import Path

LANGS = [("Java", "java", "Main.java"), ("Python", "python", "main.py"), ("C++", "cpp", "main.cpp"), ("JavaScript", "javascript", "main.js")]
HARNESS = re.compile(r"\s*(//|#) ---- test harness: not on the blog ----\s*$")
LANG_TAGS = {"#java", "#python", "#cpp", "#c++", "#javascript", "#js"}


def above(path):
    lines = Path(path).read_text().split("\n")
    cut = next((i for i, l in enumerate(lines) if HARNESS.match(l)), None)
    if cut is None:
        raise ValueError(f"{path}: no harness line")
    return "\n".join(lines[:cut]).rstrip()


def run_tests(folder, ns, work):
    """Each program reads one test per stdin line and prints one answer per line.
    ref.py gives test_inputs() and expected(line). Returns (count, errors)."""
    folder, work = Path(folder), Path(work)
    if "test_inputs" not in ns or "expected" not in ns:
        return 0, ["ref.py needs test_inputs() and expected(line)"]
    inputs = [str(x) for x in ns["test_inputs"]()]
    want = [str(ns["expected"](x)) for x in inputs]
    stdin = "\n".join(inputs) + "\n"
    work.mkdir(parents=True, exist_ok=True)
    errs = []
    for name, _, fn in LANGS:
        src = folder / "code" / fn
        if not src.exists():
            errs.append(f"{name}: code/{fn} missing")
            continue
        try:
            above(src)
        except ValueError as e:
            errs.append(str(e))
            continue
        d = work / name.replace("+", "p")
        if d.exists():
            shutil.rmtree(d)
        d.mkdir()
        shutil.copy(src, d / fn)
        cmd = {"Java": f"javac -d out {fn} && java -cp out Main", "Python": f"python3 {fn}",
               "C++": f"g++ -std=c++17 -O2 {fn} -o a.out && ./a.out", "JavaScript": f"node {fn}"}[name]
        r = subprocess.run(cmd, shell=True, cwd=d, input=stdin, capture_output=True, text=True, timeout=300)
        if r.returncode:
            errs.append(f"{name}: exit {r.returncode}: {r.stderr.strip()[-300:]}")
            continue
        got = r.stdout.rstrip("\n").split("\n") if inputs else []
        bad = [i for i, (g, w) in enumerate(zip(got, want)) if g.strip() != w.strip()]
        if len(got) != len(want):
            errs.append(f"{name}: printed {len(got)} lines for {len(want)} tests")
        elif bad:
            i = bad[0]
            errs.append(f"{name}: {len(bad)} wrong, first on input '{inputs[i][:60]}': got '{got[i][:60]}', want '{want[i][:60]}'")
    return len(inputs), errs


def pseudocode(seq):
    """The slides' pseudocode, joined: template slide, or all solution slides."""
    lines = []
    for t, s in seq:
        if t in ("template", "solution") and s.get("code"):
            lines += s["code"]["lines"]
    return "\n".join(lines)


def _q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def problem_url(p):
    if p.get("url"):
        return p["url"]
    raise ValueError(f"problem {p.get('id')} needs a 'url' (checked to open)")


def mdx(post, ns, seq, folder, tested_count, published, n_slides, video_slot, body=None):
    b = post["blog"]
    fm = ["---", f"number: {post['number']}", f"title: {_q(b.get('title', post['cover']['title'].replace(chr(10), ' ').replace('**', '')))}",
          f"slug: {post['slug']}", f"pattern: {_q(b['pattern'])}", f"section: {_q(b['section'])}", f"summary: {_q(b['summary'])}"]
    if b.get("worked"):
        fm.append(f"worked: {{ name: {_q(b['worked']['name'])}, url: {_q(b['worked']['url'])} }}")
    probs = next((s.get("problems", []) for t, s in seq if t in ("practice", "closing")), [])
    worked_name = (b.get("worked") or {}).get("name")
    items = [p for p in probs if f"{p.get('platform', 'LeetCode')} {p['id']} {p['title']}" != worked_name]
    if items:
        fm.append("practice:")
        for p in items:
            fm.append(f"  - {{ name: {_q(p.get('platform', 'LeetCode') + ' ' + str(p['id']) + ' ' + p['title'])}, url: {_q(problem_url(p))}, "
                      f"level: {p['difficulty'].lower()}, note: {_q(p.get('note', ''))} }}")
    else:
        fm.append("practice: []")
    fm.append(f"slides: {n_slides}")
    if video_slot:
        fm.append(f"video: {video_slot}")
    fm += [f"tags: [{', '.join(b['tags'])}]", f"published: {published}", "---", ""]
    body = body if body is not None else (Path(folder) / "blog.md").read_text()
    code = []
    for name, lang, fn in LANGS:
        code.append(f"## {name}\n\n```{lang}\n{above(Path(folder) / 'code' / fn)}\n```\n")
    tested = (f"{b.get('tested_what', post['topic'])} was run in Java, Python, C++ and JavaScript on {tested_count:,} inputs"
              f"{': ' + b['tested_inputs'] if b.get('tested_inputs') else ''}. Every output matched {b.get('tested_against', 'the Python reference')}."
              f"{' ' + b['tested_extra'] if b.get('tested_extra') else ''}")
    body = (body.replace("{{PSEUDOCODE}}", "```\n" + pseudocode(seq) + "\n```")
                .replace("{{CODE}}", "\n".join(code).rstrip()).replace("{{TESTED}}", tested))
    return "\n".join(fm) + "\n" + body.strip() + "\n"


def caption(post):
    c = post["caption"]
    tags = c["tags"]
    errs = []
    if not 3 <= len(tags) <= 5:
        errs.append("caption: use 3 to 5 hashtags")
    if any(t.lower() in LANG_TAGS for t in tags):
        errs.append("caption: no single-language hashtag")
    lines = [c["first"], ""] + c["lines"] + ([""] + [c["cta"]] if c.get("cta") else []) + \
            ["", "Full code in Java, Python, C++ and JavaScript: link in bio.", "", " ".join(tags)]
    return "\n".join(lines), errs


def _plain(s):
    return re.sub(r"\*\*|\[\[|\]\]|`|~", "", str(s)).replace("\n", " ")


def alt_texts(post, seq):
    out = []
    for n, (t, s) in enumerate(seq, 1):
        if s.get("alt"):
            out.append(f"Slide {n}: {s['alt']}")
            continue
        if t == "cover":
            txt = f"Cover: {_plain(s['title'])}. " + (_plain(s.get("lead", "")) or "Can you crack it with hints?")
        elif t == "video":
            v = s["video"]
            txt = f"Video: {_plain(s.get('title', ''))}. {_plain(s.get('lead', ''))} {_plain(v['final'].get('caption', ''))}"
        elif t == "pause":
            txt = "Stop here. Give it 15 minutes before the first hint."
        elif t == "bridge":
            txt = "Solved it? If you are still stuck, read the solution slowly and try again tomorrow."
        elif t in ("practice", "closing"):
            txt = "Your turn: " + ", ".join(s["learnt"]) + ". Practice: " + "; ".join(f"LeetCode {p['id']} {p['title']}" for p in s["problems"]) + "."
        else:
            txt = f"{_plain(s.get('title', ''))}. {_plain(s.get('scene') or s.get('lead') or '')}"
            for b in s.get("blocks", []):
                if b["type"] in ("boxes",) and b.get("values"):
                    txt += " Boxes: " + ", ".join(str(v) for v in b["values"] if str(v)) + "."
                if b["type"] == "bars":
                    txt += " Bars of heights " + ", ".join(map(str, b["heights"])) + "."
            if s.get("code"):
                txt += f" Pseudocode, {len(s['code']['lines'])} lines."
            if s.get("quickcheck"):
                txt += " Quick check: " + _plain(s["quickcheck"]["question"])
        out.append(f"Slide {n}: " + re.sub(r"\s+", " ", txt).strip())
    return "\n".join(out)
