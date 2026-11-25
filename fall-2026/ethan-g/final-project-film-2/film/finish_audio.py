"""Pad the opener (0.8 s lead silence) and the closer (1.0 s tail), then measure the real audio clock.

Idempotent: the unpadded voice is kept as beat-<ID>-unpad.mp3. If the beat was re-voiced since
(its mp3 is newer than the -unpad copy), the new voice becomes the -unpad source.
Run after every generate_audio_kokoro.py pass.
"""
import json, subprocess
from pathlib import Path

R = Path(__file__).resolve().parent
PAD = {"BIDEA": "adelay=800:all=1", "BEND": "apad=pad_dur=4"}   # BEND: 4 s tail holds the silent end screen
sheet = json.loads((R / "beat_sheet.json").read_text())
for b in sheet["beats"]:
    path = R / b["audio_file"]
    if b["beat_id"] in PAD:
        raw = path.with_name(path.stem + "-unpad.mp3")
        if not raw.exists() or path.stat().st_mtime > raw.stat().st_mtime + 1:
            path.replace(raw)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", PAD[b["beat_id"]],
                        "-c:a", "libmp3lame", "-b:a", "192k", str(path)], check=True)
        raw.touch()   # keep the -unpad copy newer than the padded output's source time
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                       "-of", "default=nw=1:nk=1", str(path)]))
    b["actual_duration_s"] = round(d, 3)
    if b["beat_id"] == "BDEFS":
        b["shot"]["remotion"]["props"]["durationSeconds"] = round(d, 3)
(R / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
(R / "mp3/timings.json").write_text(json.dumps({b["beat_id"]: b["actual_duration_s"] for b in sheet["beats"]}, indent=2) + "\n")
print("Measured runtime:", round(sum(b["actual_duration_s"] for b in sheet["beats"]), 2), "s")
