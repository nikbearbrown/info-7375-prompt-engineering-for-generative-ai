#!/usr/bin/env python3
"""make_srt.py — captions for the film from the final beat sheet (measured beat lengths).

    python3 make_srt.py <reel-folder> <out.srt>

Each beat's narration is split into sentence-sized cues and timed across that beat's real
length in proportion to its characters. Not burned into the picture (Gate T limits on-screen
text); it ships beside the .mp4 for accessibility.
"""
import json
import re
import sys
from pathlib import Path

reel, out = Path(sys.argv[1]), Path(sys.argv[2])
beats = json.loads((reel / "beat_sheet.json").read_text())["beats"]


def ts(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def chunks(text, limit=84):
    parts = re.split(r"(?<=[.?!:])\s+", text.replace(" S Q L", " SQL").replace("dot P Y", ".py")
                     .replace("python three", "python3"))
    outp = []
    for p in parts:
        while len(p) > limit:
            cut = p.rfind(", ", 0, limit)
            cut = cut + 1 if cut > 20 else p.rfind(" ", 0, limit)
            outp.append(p[:cut].strip())
            p = p[cut:].strip()
        if p:
            outp.append(p)
    return outp


t, n, lines = 0.0, 1, []
for b in beats:
    dur = float(b.get("render_duration_s") or b.get("actual_duration_s") or b.get("estimated_duration_s"))
    lead = float(b.get("lead_silence_s") or 0)
    cs = chunks(b["narration_text"])
    total = sum(len(c) for c in cs) or 1
    speak = max(0.5, dur - lead - float(b.get("tail_silence_s") or 0))
    start = t + lead
    for c in cs:
        d = speak * len(c) / total
        lines.append(f"{n}\n{ts(start)} --> {ts(start + d)}\n{c}\n")
        n, start = n + 1, start + d
    t += dur
out.write_text("\n".join(lines))
print(f"[srt] {n - 1} cues, {t:.1f} s -> {out}")
