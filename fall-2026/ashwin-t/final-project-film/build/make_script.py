#!/usr/bin/env python3
"""SCRIPT.md, generated from beat_sheet.json and mp3/timings.json.

The script is generated from the same file the cut is built from, so it cannot drift away from what
is actually spoken. Run it after make_sheet.py and after the audio is regenerated.
"""
import json

PARTS = [
    ("PART 1 — EXECUTIVE SUMMARY", "What it is and why it matters — not how.", "B00", "B04"),
    ("PART 2 — INTRODUCTION (prior work, then the gap)",
     "Who has tried this, what they got, and what is missing.", "B05", "B10"),
    ("PART 3 — METHODS", "How it will be built, and with what.", "B11", "B18"),
    ("PART 4 — EVALUATION", "How I will know whether it worked.", "B19", "B24"),
]
# Lines I have to re-confirm myself before submitting; the generator carries them so they cannot be
# quietly lost in a regeneration.
FLAGS = {
    "B18": "states the model-access position; re-check before submission if the seat or an API key changes",
    "B24": "says *no TraceCase code exists yet*; must change if any TraceCase code is written before submission",
}

sheet = json.load(open("beat_sheet.json"))
times = json.load(open("mp3/timings.json"))
beats = {b["beat_id"]: b["narration_text"] for b in sheet["beats"]}
ids = [b["beat_id"] for b in sheet["beats"]]
total = sum(times[i] for i in ids)

out = [
    "# TraceCase — Final Project Film",
    "## Narration, exactly as spoken in the cut",
    "",
    "**This file is generated from `beat_sheet.json`, which is the file the cut is built from.**",
    "It is the shipped narration, not a draft — the wording, the beat numbering and the running",
    "order below all match `final/tracecase-final.mp4` line for line.",
    "",
    f"{len(ids)} beats · {int(total // 60)}:{total % 60:04.1f} ({total:.2f}s of narration) · narration-clocked ·",
    "four parts in the order the brief asks for. The assignment's ceiling is 240s.",
    "Every factual claim about other people's work is sourced in [FACTCHECK.md](FACTCHECK.md).",
    "Lines marked ⚠️ are mine to re-confirm before submission.",
    "",
    "---",
]
for title, blurb, lo, hi in PARTS:
    sel = [i for i in ids if lo <= i <= hi]
    secs = sum(times[i] for i in sel)
    out += ["", f"## {title}", f"*{blurb} — {len(sel)} beats, {secs:.1f}s.*", ""]
    for i in sel:
        out += [f"**{i}** · {times[i]:.2f}s", "", f"> {beats[i]}"]
        if i in FLAGS:
            out += [">", f"> ⚠️ {FLAGS[i]}"]
        out += [""]
    out += ["---"]

open("SCRIPT.md", "w").write("\n".join(out).rstrip() + "\n")
print(f"SCRIPT.md written — {len(ids)} beats, {total:.2f}s")
