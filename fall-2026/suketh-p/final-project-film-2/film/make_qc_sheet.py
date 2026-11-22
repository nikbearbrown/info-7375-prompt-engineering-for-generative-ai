#!/usr/bin/env python3
"""make_qc_sheet.py: qc-sheet.png, one frame at 85 % of each beat of the master, labelled by beat id.

The toolkit's own review sheet (written by `art run`) samples each beat's midpoint. This one samples late, at 85 %,
where a key picture that lands in the last half-second would still be missing (October's lesson: the gates cannot
see that). Beat starts come from the measured narration, rounded up to whole frames exactly as compile.py does.
Usage: python3 make_qc_sheet.py [path/to/master.mp4]   (default: exports/landscape/<slug>.mp4)
"""
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sheet = json.loads((HERE / "beat_sheet.json").read_text())
slug = sheet["metadata"]["slug"]
fps = int(sheet["metadata"].get("fps", 24))
mp4 = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "exports" / "landscape" / f"{slug}.mp4"
FRAC, TW, TH, COLS = 0.85, 768, 432, 4

try:
    font = ImageFont.truetype(str(HERE.parent / "brutalist.art" / "runtime" / "fonts" / "Inter" / "static" /
                                  "Inter_28pt-Medium.ttf"), 22)
except OSError:
    font = ImageFont.load_default()

tiles, t0 = [], 0.0
with tempfile.TemporaryDirectory() as tmp:
    for b in sheet["beats"]:
        dur = math.ceil(float(b["actual_duration_s"]) * fps - 1e-8) / fps
        t = t0 + FRAC * dur
        png = Path(tmp) / f"{b['beat_id']}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(mp4), "-frames:v", "1",
                        "-vf", f"scale={TW}:{TH}", str(png)], check=True)
        im = Image.open(png).convert("RGB")
        d = ImageDraw.Draw(im)
        tag = f"{b['beat_id']}  @85%  {t:6.2f}s"
        d.rectangle([0, TH - 34, 12 + int(d.textlength(tag, font=font)), TH], fill=(20, 20, 20))
        d.text((6, TH - 30), tag, font=font, fill=(255, 255, 255))
        tiles.append(im)
        t0 += dur
rows = (len(tiles) + COLS - 1) // COLS
out = Image.new("RGB", (COLS * TW, rows * TH), (30, 27, 24))
for i, im in enumerate(tiles):
    out.paste(im, ((i % COLS) * TW, (i // COLS) * TH))
out.save(HERE / "qc-sheet.png")
print(f"qc-sheet.png: {len(tiles)} beats at 85 % of {mp4.name} (total {t0:.2f} s)")
