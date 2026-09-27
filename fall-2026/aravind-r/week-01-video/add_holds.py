"""Add a silent hold after each beat's narration, so the last reveal stays on screen long enough to read.

Usage (after generate_audio_kokoro.py, before align.py and ./art run):
    python3 add_holds.py

Reads `hold_after_s` from each beat in beat_sheet.json, pads mp3/beat-<ID>.mp3 with that much
silence, and writes the new length back to mp3/timings.json and the beat's actual_duration_s,
which is the clock that compile.py, remotion_scenes.py and scenes.py all read. The unpadded
speech length is kept in mp3/timings.raw.json, so re-running (or changing a hold) never stacks
padding. Why a script and not hand edits: the toolkit ignores lead_silence_s/tail_silence_s,
and its rule is that timing is regenerated, never hand-patched.
"""
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"


def duration(path):
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


sheet_path = HERE / "beat_sheet.json"
sheet = json.loads(sheet_path.read_text())
timings_path = HERE / "mp3" / "timings.json"
timings = json.loads(timings_path.read_text())
raw_path = HERE / "mp3" / "timings.raw.json"
raw = json.loads(raw_path.read_text()) if raw_path.exists() else {}

for beat in sheet["beats"]:
    bid = beat["beat_id"]
    hold = float(beat.get("hold_after_s", 0))
    mp3 = HERE / "mp3" / f"beat-{bid}.mp3"
    current = duration(mp3)
    prev = raw.get(bid)
    # if the file is exactly a previous raw+hold, its speech length is that raw value
    speech = prev["speech"] if prev and abs(current - (prev["speech"] + prev["hold"])) < 0.08 else current
    target = speech + hold
    if abs(current - target) > 0.03:
        tmp = mp3.with_suffix(".tmp.mp3")
        subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(mp3), "-af", "apad", "-t", f"{target:.3f}",
                        "-c:a", "libmp3lame", "-q:a", "2", str(tmp)], check=True)
        tmp.replace(mp3)
    final = round(duration(mp3), 2)
    raw[bid] = {"speech": round(speech, 3), "hold": hold}
    timings[bid] = final
    beat["actual_duration_s"] = final
    print(f"{bid}: speech {speech:6.2f}s + hold {hold:.1f}s = {final:6.2f}s")

raw_path.write_text(json.dumps(raw, indent=2) + "\n")
timings_path.write_text(json.dumps(timings, indent=2) + "\n")
sheet_path.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
print(f"total {sum(timings[b['beat_id']] for b in sheet['beats']):.2f}s")
