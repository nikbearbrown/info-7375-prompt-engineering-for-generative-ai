#!/usr/bin/env python3
"""make_script_md.py: SCRIPT.md, the review copy of the narration, generated from film/beat_sheet.json.

The narration lives in film/make_sheet.py. This file is only for reading and marking up. Written by Claude Code,
2026-11-21.
Run: python3 tools/make_script_md.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sheet = json.loads((ROOT / "film" / "beat_sheet.json").read_text())
beats = sheet["beats"]
draft = sheet["metadata"].get("draft", False)

out = ["# SCRIPT — Fine Print (Final Project Film)", ""]
out.append("**Drafted by Claude Code from the records in [FACTCHECK.md](FACTCHECK.md); approved by the student on "
           "2026-11-21 (\"Approve it\").** B07 and B16 use the student's own words from Frictional entry 1, and B17 is "
           "the student's own bar, word for word. The narration is spoken in the first person, as the student, by the "
           "synthesized voice am_eric.")
out.append("")
out.append("Stamps (top left on screen) say what each picture is: `real · …` means it ran or was checked; "
           "`constructed · not built` means it's the plan.")
out.append("")

part, t = None, 0.0
for b in beats:
    p = b.get("on_screen_part") or "Close"
    if p != part:
        out += [f"## {p}", ""]
        part = p
    dur = b.get("actual_duration_s") or (b["estimated_duration_s"] + b.get("lead_silence_s", 0) +
                                         b.get("tail_silence_s", 0))
    kind = "measured" if b.get("actual_duration_s") else "estimated"
    stamp = b.get("on_screen_status", "—")
    out.append(f"**{b['beat_id']}** · {t:4.0f}–{t + dur:.0f} s ({kind}) · stamp: `{stamp}`")
    out.append("")
    out.append(f"> {b['narration_text']}")
    out.append("")
    t += dur
    if b["beat_id"] == "B16" and not any(x["beat_id"] == "B17" for x in beats):
        out += ["**B17** · *your bar — not in the draft*", "",
                "> *Written by you: what result would tell you Fine Print worked, and what would tell you it didn't, "
                "and how many postings you'll label.*", ""]

out.append(f"Total so far: {t:.0f} s ({t / 60:.1f} min) of a 300 s cap.")
(ROOT / "SCRIPT.md").write_text("\n".join(out) + "\n")
print(f"SCRIPT.md: {len(beats)} beats, {t:.0f} s")
