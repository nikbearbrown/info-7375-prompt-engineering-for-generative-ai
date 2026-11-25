#!/usr/bin/env python3
"""tools/timeline.py: writes TIMELINE.md (scene-by-scene start, end, length, section, narration) from the real audio."""
import json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
scenes = json.loads((ROOT / "src/config/scenes.json").read_text())
dur = json.loads((ROOT / "src/config/durations.json").read_text())
SEC = {"summary": "01 Executive summary", "introduction": "02 Introduction", "methods": "03 Methods", "evaluation": "04 Evaluation", "closing": "Closing"}
fmt = lambda s: f"{int(s // 60)}:{s % 60:04.1f}"
rows, t = [], 0.0
for s in scenes:
    n = math.ceil((dur[s["id"]] + s.get("padSeconds", 0.6)) * 30) / 30
    narr = (ROOT / f"src/narration/{s['id']}.txt").read_text().strip()
    rows.append(f"| {s['id']} | {SEC[s['section']]} | {fmt(t)} | {fmt(t + n)} | {n:.1f}s | {narr} |")
    t += n
out = ["# TIMELINE: ProductLens AI project film", "",
       f"Generated from the measured narration (src/config/durations.json). Total: **{fmt(t)}** at 30 fps, 1920×1080.",
       "Each scene lasts exactly as long as its narration plus a short pause (padSeconds in src/config/scenes.json).", "",
       "| Scene | Section | Start | End | Length | Narration |", "|---|---|---|---|---|---|"] + rows
(ROOT / "TIMELINE.md").write_text("\n".join(out) + "\n")
print(f"TIMELINE.md: {len(rows)} scenes, {fmt(t)}")
