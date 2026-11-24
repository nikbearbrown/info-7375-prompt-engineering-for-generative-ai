#!/usr/bin/env python3
"""sync_durations.py — write each beat's measured MP3 length into beat_sheet.json.

Run from the reel folder after any audio change (re-voice, BOUT padding):
    python3 sync_durations.py
Sets actual_duration_s (ffprobe, 2 decimals) and audio_file ("mp3/beat-<ID>.mp3"),
the same format the toolkit's audio script writes.
"""
import json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
path = HERE / "beat_sheet.json"
sheet = json.loads(path.read_text())
total = 0.0
for b in sheet["beats"]:
    rel = f"mp3/beat-{b['beat_id']}.mp3"
    mp3 = HERE / rel
    if not mp3.exists():
        print(f"{b['beat_id']}: MISSING {rel}")
        continue
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "csv=p=0", str(mp3)], capture_output=True, text=True, check=True).stdout)
    b["actual_duration_s"], b["audio_file"] = round(d, 2), rel
    total += d
    print(f"{b['beat_id']:6} {d:6.2f}s")
path.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
print(f"total narration {total:.1f}s ({int(total//60)}:{int(total%60):02d})")
