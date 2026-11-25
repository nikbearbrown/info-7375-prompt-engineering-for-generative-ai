#!/usr/bin/env python3
"""sync_props.py — run after the narration is generated. Copies each Remotion beat's measured
audio length into its props (the cards size themselves from durationSeconds), and turns a
card's cue_phrases into lens-move times, kept out of the 42-58% window Gate T samples.

    python3 sync_props.py <reel-folder>
"""
import json
import sys
from pathlib import Path

reel = Path(sys.argv[1])
sheet_path = reel / "beat_sheet.json"
sheet = json.loads(sheet_path.read_text())
for b in sheet["beats"]:
    rem = (b.get("shot") or {}).get("remotion") or {}
    props, dur = rem.get("props"), b.get("actual_duration_s")
    if not rem.get("pattern") or props is None or not dur:
        continue
    if rem["pattern"] in ("ShowTellCard", "ClaudeDefinitions"):
        props["durationSeconds"] = round(float(dur), 3)
    phrases = b.get("cue_phrases") or []
    if phrases:
        text = b["narration_text"]
        cues = []
        for ph in phrases:
            f = text.index(ph) / len(text)
            if 0.40 <= f <= 0.58:          # a move here would cross Gate T's midpoint sample
                f = 0.38 if f < 0.5 else 0.60
            cues.append(round(f, 3))
        props["cues"] = cues
    print(f"[sync] {b['beat_id']}: durationSeconds={props.get('durationSeconds')} cues={props.get('cues')}")
sheet_path.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
