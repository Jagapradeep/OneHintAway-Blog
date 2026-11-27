"""Draft a video script from a post kit folder: python3 youtube/engine/draft.py NN-slug [--force]

Writes youtube/scripts/NN-slug/script.json with everything that can be copied from the post (story, the
motion video's steps, the code with line-by-line reveals, the trap, the cost, practice, chapters, links,
Shorts). Every line that needs judgment (hooks, the spoken explanation, tones, the hack Short) is a
"TODO: ..." line, and yt.py refuses a script that still holds a TODO or _draft_notes, so a draft can
never be rendered unreviewed. Numbers stay as {{expressions}} from the post's ref.py.
"""
import json, sys
from pathlib import Path
import kitload as K

ROOT = Path(__file__).resolve().parents[1]


def code_of(slide):
    if slide.get("code"):
        return slide["code"]["lines"]
    return next((b["lines"] for b in slide.get("blocks", []) if b.get("type") == "code"), None)


def code_scene(sid, label, title, lines, src, chapter=None):
    """Reveal the code in chunks of about three lines, one voice line per chunk."""
    say, k, n = [], 1, len(lines)
    while k <= n:
        end = min(n, k + 2 if k > 1 else 1)
        say.append({"say": f"TODO: explain line{'s' if end > k else ''} {k}{f' to {end}' if end > k else ''} in the order you'd teach it",
                    "upto": end, "hl": list(range(k, end + 1))})
        k = end + 1
    sc = {"id": sid, "layout": "code", "label": label, "title": title, "lines_from": src, "say": say}
    if chapter:
        sc["chapter"] = chapter
    return sc


def kit_steps(tl, every=False):
    steps, seen = {}, set()
    for i, st in enumerate(tl["states"]):
        cap = st.get("caption") or ""
        if cap and (every or cap not in seen):
            steps[str(i)] = f"TODO: say this step aloud (slide caption: {cap})"
            seen.add(cap)
    return steps


def example_values(raw):
    """The post's tiny example as a flat list, for a picture opening (None when it isn't a plain array)."""
    for s in raw["slides"]:
        if s["type"] == "video" and isinstance(s["video"].get("values"), list):
            v = s["video"]["values"]
            if v and all(isinstance(x, (int, float, str)) and len(str(x)) <= 3 for x in v) and len(v) <= 8:
                return v
    return None


def picture_hook(vals, think=3):
    return {"id": "hook", "layout": "viz", "chapter": "The problem", "values": vals, "under": list(range(len(vals))),
            "tag": "TODO: the goal in a few characters, e.g. target = 10",
            "states": [{"at": 0}, {"at": 2, "note": "TODO: two or three words for the slow way"},
                       {"at": 4, "note": "TODO: two or three words for the result"}],
            "say": [{"say": "TODO: the problem as a question about this picture", "tone": "question"}, {"think": think},
                    "TODO: the slow way, shown on the picture (a sweep over pairs, a scan)",
                    {"say": "TODO: why the slow way hurts", "tone": "low"},
                    {"say": "TODO: name the result, keep the method a secret until later", "tone": "reveal"},
                    "TODO: what the viewer will be able to do by the end (honest)"]}


def trap_edit(template, trap):
    """Find the template line the trap changes, so the trap Short shows the whole function with it swapped."""
    right = [c.strip() for c in trap["right"]["code"]]
    for i, line in enumerate(template):
        if right and line.strip() == right[0] and len(trap["wrong"]["code"]) == 1:
            indent = line[: len(line) - len(line.lstrip())]
            return {str(i + 1): indent + trap["wrong"]["code"][0].strip()}, i + 1
    return None, None


def draft(slug, force=False):
    raw = json.loads((K.KIT / "posts" / slug / "post.json").read_text())
    _, _, _, tl = K.load(slug)
    kind, cover = raw["kind"], raw["cover"]
    by = {}
    for s in raw["slides"]:
        by.setdefault(s["type"], []).append(s)
    notes = ["Rewrite every TODO line as spoken English (no symbols: put the written form in 'show') and delete this list. One sentence becomes one caption: keep sentences under 88 characters (58 in Shorts). Letters said on their own get their sound: [a](/ˈeɪ/), and the caption shows \"a\".",
             "Teach, don't summarise: one idea per voice line, code revealed in the order you explain it.",
             "Add tones to a fifth to a half of the lines (question, reveal, lift, warm, low, pause), never every line.",
             "If the post builds on an earlier one, add a 'prereq' code scene with lines_from that post and say which video to watch.",
             "Add a dry-run table or boxes scene if the walk doesn't show every value."]
    vals = example_values(raw)
    if vals:
        L = [picture_hook(vals)]
        notes.append("Hook: frame 1 is the problem as a picture (no title card). Ask, give 3 s to think, show the slow way on the picture, "
                     "then name the result but keep the method for later (an open loop the video closes). Add a sweep or arcs to the states.")
    else:
        L = [{"id": "hook", "layout": "big", "chapter": "The problem", "title": "TODO: the problem as a short question",
              "items": [{"text": "TODO: the input, drawn small (mono)", "style": "mono", "at": 0}],
              "say": [{"say": "TODO: the problem as a question", "tone": "question"}, {"think": 3}, "TODO: the slow way",
                      {"say": "TODO: the result, method kept for later", "tone": "reveal"}]}]
        notes.append("Hook: this post's example isn't a plain array, so the hook is a 'big' scene. Show the input itself, never a sentence about it.")
    st = by.get("story", [{}])[0]
    box = next((b for b in st.get("blocks", []) if b.get("type") == "boxes"), None) if st else None
    if st and box:
        L.append({"id": "story", "layout": "viz", "chapter": "The idea", "label": "THE STORY", "title": st["title"], "values": box["values"],
                  "states": [{"at": 0}, {"at": 1, "steel": box.get("steel", []), "gold": box.get("gold", []), "note": "TODO: a two-to-four-word label"}],
                  "say": [f"TODO: tell the story aloud over the picture: {st.get('scene', '')}", "TODO: link the story to the picture"]})
    elif st:
        L.append({"id": "story", "layout": "big", "chapter": "The idea", "label": "THE STORY", "title": st["title"],
                  "items": [{"text": "TODO: a picture of the story (mono drawing or a few words), not the story's sentences", "style": "mono", "at": 0}],
                  "say": [f"TODO: tell the story aloud: {st.get('scene', '')}", "TODO: link the story to the idea"]})
    if kind == "challenge":
        pr = by["problem"][0]
        L.append({"id": "problem", "layout": "list", "label": "THE REAL PROBLEM", "title": pr["title"], "cols": 1,
                  "items": [{"head": "THE PROBLEM", "text": pr.get("lead", "")}], "say": ["TODO: state the problem and its example"]})
        L.append({"id": "pause", "layout": "pause", "text": by["pause"][0].get("try_first", "Try it yourself first."),
                  "say": ["Pause the video and try it yourself."]})
        for i, h in enumerate(by.get("hint", []), 1):
            L.append({"id": f"hint{i}", "layout": "list", "chapter": f"Hint {i}", "label": f"HINT {i}", "title": h["title"], "cols": 1,
                      "items": [{"head": f"HINT {i}", "text": h.get("lead", ""), "accent": "gold"}],
                      "say": [f"TODO: hint {i} aloud: {h.get('lead', '')}"]})
            L.append({"id": f"try{i}", "layout": "pause", "text": "Try again with this hint.", "say": ["Pause, and try again with this hint."]})
    L.append({"id": "walk", "layout": "kit", "chapter": "Watch it work", "label": "WATCH IT WORK",
              "title": next((s["title"] for s in by.get("video", [])), "Watch it work"), "steps": kit_steps(tl)})
    if kind == "concept":
        for j, ex in enumerate(by.get("extra", [])):
            if code_of(ex):
                L.append(code_scene(f"helper{j + 1}", ex.get("label", "THE HELPER"), ex["title"], code_of(ex), {"slide": "extra", "n": j}, "The code"))
        t = by["template"][0]
        L.append(code_scene("code", "THE CODE", t["title"], code_of(t), {"slide": "template"},
                            None if any(s.get("chapter") == "The code" for s in L) else "The code"))
        trap_slide = by["trap"][0]
    else:
        for j, sol in enumerate(by.get("solution", [])):
            L.append(code_scene(f"solution{j + 1}", f"THE SOLUTION · PART {j + 1}", sol["title"], code_of(sol),
                                {"slide": "solution", "n": j}, "The code" if j == 0 else None))
        trap_slide = None
    if trap_slide:
        tr = trap_slide["trap"]
        L.append({"id": "trap", "layout": "viz", "chapter": "The trap", "label": "THE TRAP", "title": trap_slide["title"],
                  "values": vals or [0], "tag": f"TODO: the trap's own input as a short tag ({tr.get('call', '')})",
                  "panels": [{"head": "WRONG", "accent": "red", "code": tr["wrong"]["code"], "bad": [0], "result": tr["wrong"]["result"], "at": 0, "dim_at": 2},
                             {"head": "RIGHT", "accent": "gold", "code": tr["right"]["code"], "good": [0], "result": tr["right"]["result"], "at": 2}],
                  "states": [{"at": 0, "note": "TODO: wrong version, first step"}, {"at": 1, "red": [], "note": "TODO: where it goes wrong"},
                             {"at": 2, "note": "TODO: right version, first step"}, {"at": 3, "gold": [], "note": "TODO: the right result"}],
                  "say": ["TODO: name the trap, then the input it fails on", {"say": "TODO: walk the wrong version to its wrong result", "tone": "low"},
                          "TODO: the fix, walked on the same input", {"say": "TODO: the right result", "tone": "reveal"}]})
        notes.append("Trap: one frame. Code cards on the left (wrong line in red, the wrong card fades when the fix appears), the trap's own input on the right, walked for both versions.")
    cost = (trap_slide or {}).get("cost") or next((s["cost"] for s in by.get("solution", []) if s.get("cost")), None)
    if cost:
        L.append({"id": "cost", "layout": "table", "label": "THE COST", "title": "What it costs", "head": ["", "COST"],
                  "widths": ["1.4fr", "1fr"], "mono": [1], "rows": [[c["label"], c["value"]] for c in cost["items"]],
                  "together": True, "say": [f"TODO: the cost aloud ({cost.get('note', '')})"]})
    prac = (by.get("practice") or by.get("closing"))[0]["problems"]
    if vals:
        L.append({"id": "recap", "layout": "viz", "chapter": "Your turn", "label": "WORKED EXAMPLE", "values": vals, "under": list(range(len(vals))),
                  "tag": "TODO: the goal, as in the hook", "states": [{"at": 0, "gold": [], "note": "TODO: answer · how · cost"}],
                  "say": ["TODO: recap the worked example on the picture, in two or three sentences"]})
    L.append({"id": "end", "layout": "end", "title": "Your turn",
              "covered": [{"site": "LeetCode", "id": 0, "title": "TODO: the problem solved in this video (LeetCode or GeeksforGeeks)", "level": "Easy", "at": 0}],
              "practice": [{"id": p["id"], "title": p["title"], "level": p["difficulty"], "note": p.get("note", ""), "at": i + 1} for i, p in enumerate(prac)],
              "say": ["TODO: In this video, we solved <problem>, with <how>."] + [f"TODO: why {p['title']} uses this pattern, and the first step (short sentences)" for p in prac]})

    shorts = []
    tmpl = code_of(by["template"][0]) if kind == "concept" else None
    if trap_slide and tmpl:
        edit, line = trap_edit(tmpl, trap_slide["trap"])
        if not edit:
            notes.append("Trap Short: the trap line isn't a single template line; pick the lines to show and set lines_from.edit by hand.")
        shorts.append({"kind": "trap", "title": trap_slide["title"], "scenes": [
            {"id": "bug", "layout": "code", "label": "THE TRAP", "title": "Spot the bug",
             "lines_from": {"slide": "template", **({"edit": edit} if edit else {})},
             "say": [{"say": "TODO: the hook, a question about the whole function", "tone": "question", "upto": len(tmpl)},
                     {"think": 3},
                     {"say": "TODO: 'Here it is.' then the failing input and the wrong result", "upto": len(tmpl), **({"bad": [line]} if line else {})}]},
            {"id": "fix", "layout": "code", "label": "THE FIX", "title": "The fix", "lines_from": {"slide": "template"},
             "say": [{"say": "TODO: the fix and the right result", "upto": len(tmpl), **({"hl": [line]} if line else {})}]}]})
    if kind == "concept":
        shorts.append({"kind": "hack", "title": "TODO: one coding trick tied to this pattern", "scenes": [
            {"id": "hack", "layout": "code", "label": "CODING HACK", "title": "TODO: hack title", "lines": ["TODO: code"],
             "say": [{"say": "TODO: the hook", "tone": "lift", "upto": 1}]}]})
        notes.append("Hack Short: write it from scratch (one real time-saver or bug-avoider for this pattern), or delete it if nothing honest fits.")
    bh = ({"id": "hook", "layout": "viz", "values": vals, "tag": "TODO: the goal in a few characters", "states": [{"at": 0}],
           "say": [{"say": "TODO: the problem as a question about the picture", "tone": "question"}, {"think": 2}, "TODO: one line into the walk"]}
          if vals else
          {"id": "hook", "layout": "big", "title": "TODO: the problem in a few words", "items": [{"text": "TODO: the input (mono)", "style": "mono", "at": 0}],
           "say": [{"say": "TODO: the hook", "tone": "question"}]})
    shorts.append({"kind": "booster", "title": raw["topic"], "scenes": [
        bh,
        {"id": "walk", "layout": "kit", "label": "WATCH", "title": "TODO: short title", "steps": kit_steps(tl)}]})
    notes.append("Booster Short: keep 2 to 4 walk steps (delete the rest from 'steps') so it stays under 58 seconds.")

    ids = ", ".join(f"LeetCode {p['id']}" for p in prac)
    tags = [t.lstrip("#") for t in raw.get("caption", {}).get("tags", [])]
    spec = {"_draft_notes": notes, "number": raw["number"], "slug": raw["slug"], "post": slug, "kind": kind,
            "long": {"scenes": L}, "shorts": shorts,
            "youtube": {"title": f"TODO: {raw['topic']}: searchable title, honest, under 70 characters",
                        "description": f"TODO: two sentences on what the video teaches.\n\n{{CHAPTERS}}\n\nCode in Java, Python, C++ and JavaScript: https://onehintaway.com/posts/{raw['slug']}/\nPractice: {ids}\n\n" + " ".join("#" + t for t in tags[:3]),
                        "tags": tags}}
    out = ROOT / "scripts" / slug / "script.json"
    if out.exists() and not force:
        raise SystemExit(f"{out} exists; pass --force to overwrite")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
    todo = json.dumps(spec).count("TODO")
    print(f"{out}: {len(L)} long scenes, {len(shorts)} Shorts, {todo} TODO lines to write")


if __name__ == "__main__":
    draft(sys.argv[1], "--force" in sys.argv)
