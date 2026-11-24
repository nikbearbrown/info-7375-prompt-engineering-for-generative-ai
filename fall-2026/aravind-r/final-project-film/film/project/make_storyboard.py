#!/usr/bin/env python3
"""make_storyboard.py — the storyboard contact sheet: one still per beat (each beat's last frame), 5 across.

Since 23 Nov 2026 (pre-Phase-5 review) the stills are grabbed from the final master, aravind-r-readback-project-film.mp4,
at each beat's last frame (beat end − 0.06 s), into one folder as <SceneClass>.png and BOUT.png. (Phase 2 used
`manim -s` stills and a `remotion still` of the outro.)

Usage: python3 make_storyboard.py <frames-folder>   → writes storyboard.png next to this file.
"""
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
frames = sys.argv[1]
beats = json.load(open(os.path.join(HERE, "beat_sheet.json")))["beats"]
total = sum(b["actual_duration_s"] for b in beats)
font = ImageFont.truetype(os.path.expanduser("~/Library/Fonts/EBGaramond-Regular.ttf"), 26)
W, H, CAP, M, COLS = 640, 360, 44, 18, 5
rows = (len(beats) + COLS - 1) // COLS
out = Image.new("RGB", (COLS * W + (COLS + 1) * M, rows * (H + CAP) + (rows + 1) * M + 60), (61, 57, 41))
d = ImageDraw.Draw(out)
d.text((M, 14), f"Readback project film · storyboard from the final master, last frame of each beat · {len(beats)} beats · "
                f"{total:.1f} s · 23 Nov 2026", font=font, fill=(242, 240, 233))
for k, b in enumerate(beats):
    name = "BOUT" if b["beat_id"] == "BOUT" else b["shot"]["manim"]["class"]
    im = Image.open(os.path.join(frames, f"{name}.png")).convert("RGB").resize((W, H), Image.LANCZOS)
    x, y = M + (k % COLS) * (W + M), 60 + M + (k // COLS) * (H + CAP + M)
    out.paste(im, (x, y))
    part = "Outro" if b["beat_id"] == "BOUT" else b["part_label"].split(" · ")[-1]
    d.text((x + 4, y + H + 6), f"{b['beat_id']} · {part} · {b['actual_duration_s']:.1f} s", font=font, fill=(242, 240, 233))
out.save(os.path.join(HERE, "storyboard.png"))
print("storyboard.png", out.size)
