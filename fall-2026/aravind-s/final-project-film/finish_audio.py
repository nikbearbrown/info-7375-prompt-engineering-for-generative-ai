#!/usr/bin/env python3
"""finish_audio.py: pad the opener and the outro, then measure the real audio clock.

Run after generate_audio_kokoro.py and before align.py. Idempotent: a padded
file is recognised by its recorded hash, so re-running never pads twice, and a
freshly re-voiced beat is picked up as the new raw take.

- BIDEA gets 0.8 s of lead silence (the writer starts before the voice).
- BOUT gets a 1.0 s silent tail.
- Remotion beats get durationSeconds = the measured audio.
"""
import hashlib
import json
import subprocess
from pathlib import Path

R = Path(__file__).resolve().parent
PADS = {"BIDEA": "adelay=800:all=1", "BOUT": "apad=pad_dur=1"}
STATE = R / "mp3" / "pad-state.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def duration(path: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)]
    )
    return round(float(out), 3)


sheet = json.loads((R / "beat_sheet.json").read_text())
state = json.loads(STATE.read_text()) if STATE.exists() else {}
for b in sheet["beats"]:
    path = R / b["audio_file"]
    bid = b["beat_id"]
    if bid in PADS:
        raw = path.with_name(path.stem + "-unpad.mp3")
        if state.get(bid) != sha(path):  # not our padded output: this is a new raw take
            path.replace(raw)
            subprocess.run(
                ["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", PADS[bid], "-c:a", "libmp3lame", "-b:a", "192k", str(path)],
                check=True,
            )
            state[bid] = sha(path)
    b["actual_duration_s"] = duration(path)
    remotion = (b.get("shot") or {}).get("remotion")
    if remotion:
        remotion.setdefault("props", {})["durationSeconds"] = b["actual_duration_s"]

STATE.write_text(json.dumps(state, indent=2) + "\n")
(R / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
(R / "mp3" / "timings.json").write_text(
    json.dumps({b["beat_id"]: b["actual_duration_s"] for b in sheet["beats"]}, indent=2) + "\n"
)
total = sum(b["actual_duration_s"] for b in sheet["beats"])
print(f"measured runtime: {total:.1f} s ({int(total // 60)}:{total % 60:04.1f})")
