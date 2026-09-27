"""Append the sheet's inter_beat_gap_s of silence to every narrated beat's mp3 except the
last beat, re-measure, and write actual_duration_s + mp3/timings.json. Run after
generate_audio_kokoro.py (which rewrites the mp3s).

Rerun-safe: after padding, the padded mp3's duration is stored in gap_padded_mp3_s. A beat whose
current mp3 still measures that duration is already padded and is skipped, so a rerun never
stacks a second gap; a freshly regenerated mp3 measures shorter and gets padded.
  python pad_gaps.py              # every eligible beat
  python pad_gaps.py --only B07   # just these beats
"""
import argparse, json, subprocess
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("--only", nargs="*")
a = ap.parse_args()

reel = Path(__file__).resolve().parent
sheet_p = reel / "beat_sheet.json"
sheet = json.loads(sheet_p.read_text(encoding="utf-8"))
gap = float(sheet["metadata"]["inter_beat_gap_s"])
timings_p = reel / "mp3" / "timings.json"
timings = json.loads(timings_p.read_text()) if timings_p.exists() else {}


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout)


for b in sheet["beats"][:-1]:
    bid = b["beat_id"]
    if b.get("audio_policy") == "silence" or (a.only and bid not in a.only):
        continue
    mp3 = reel / b["audio_file"]
    if b.get("gap_padded_mp3_s") == round(dur(mp3), 2):
        print(f"{bid}: already padded ({b['gap_padded_mp3_s']}s) - skipped")
        continue
    tmp = mp3.with_suffix(".pad.mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-af", f"apad=pad_dur={gap}",
                    "-c:a", "libmp3lame", "-q:a", "2", str(tmp)], check=True)
    tmp.replace(mp3)
    b["actual_duration_s"] = timings[bid] = b["gap_padded_mp3_s"] = round(dur(mp3), 2)
    b["gap_padded_s"] = gap
    print(f"{bid}: {b['actual_duration_s']}s (incl. {gap}s gap)")
sheet_p.write_text(json.dumps(sheet, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
timings_p.write_text(json.dumps(timings, indent=1))
