"""Contact sheet of a build for review: python3 youtube/engine/sheet.py youtube/build/NN-slug [out.png]"""
import sys
from pathlib import Path
from PIL import Image

def main(build, out=None):
    rows = []
    for d in sorted(p for p in Path(build).iterdir() if p.is_dir()):
        ims = [Image.open(f) for f in sorted(d.glob("scene-*.png"))]
        if not ims:
            continue
        w = 520 if ims[0].width > ims[0].height else 220
        rows.append([im.resize((w, round(im.height * w / im.width))) for im in ims])
    per = 4
    lines = [r[i:i + per] for r in rows for i in range(0, len(r), per)]
    W = max(sum(i.width + 6 for i in l) for l in lines); H = sum(l[0].height + 6 for l in lines)
    sheet = Image.new("RGB", (W, H), (45, 45, 45)); y = 0
    for l in lines:
        x = 0
        for im in l:
            sheet.paste(im, (x, y)); x += im.width + 6
        y += l[0].height + 6
    out = out or str(Path(build) / "sheet.png"); sheet.save(out); print(out, sheet.size)

if __name__ == "__main__":
    main(*sys.argv[1:])
