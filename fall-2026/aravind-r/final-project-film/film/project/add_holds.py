"""Trim each beat's clip edges and add a silent hold after its narration, so the gaps between beats are short and even.

Usage (after generate_audio_kokoro.py, before align.py and ./art run):
    python3 add_holds.py

For each beat in beat_sheet.json: cut mp3/beat-<ID>.mp3 back to its speech (dropping any earlier hold), trim the
silence Kokoro leaves at both edges down to EDGE_KEEP seconds, then pad `hold_after_s` of silence. The silence a
viewer hears between two beats is therefore hold + 2 × EDGE_KEEP. The new length is written to mp3/timings.json and
the beat's actual_duration_s, which is the clock that compile.py, remotion_scenes.py and scenes.py all read. The
speech length (after trimming) is kept in mp3/timings.raw.json, so re-running (or changing a hold) never stacks
padding or trims twice. Why a script and not hand edits: the toolkit ignores lead_silence_s/tail_silence_s, and its
rule is that timing is regenerated, never hand-patched.
"""
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"
EDGE_KEEP = 0.05          # seconds of silence kept at each clip edge
FLOOR_DB = -50            # what counts as silence at the edges


def duration(path):
    out = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def ff(*args):
    subprocess.run([FFMPEG, "-y", "-v", "error", *args], check=True)


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
    padded = prev and abs(current - (prev["speech"] + prev["hold"])) < 0.08
    speech = prev["speech"] if padded else current
    if padded and prev.get("trimmed") and abs(prev["hold"] - hold) < 0.01:
        final = round(current, 2)                      # already trimmed and padded with this hold: leave the file alone
    else:
        wav = mp3.with_suffix(".edit.wav")
        edge = (f"silenceremove=start_periods=1:start_threshold={FLOOR_DB}dB:start_silence={EDGE_KEEP}")
        if prev and prev.get("trimmed"):
            ff("-i", str(mp3), "-af", f"atrim=0:{speech:.3f}", str(wav))
        else:
            ff("-i", str(mp3), "-af", f"atrim=0:{speech:.3f},{edge},areverse,{edge},areverse", str(wav))
        speech = duration(wav)
        tmp = mp3.with_suffix(".tmp.mp3")
        ff("-i", str(wav), "-af", "apad", "-t", f"{speech + hold:.3f}", "-c:a", "libmp3lame", "-q:a", "2", str(tmp))
        tmp.replace(mp3)
        wav.unlink()
        final = round(duration(mp3), 2)
    raw[bid] = {"speech": round(speech, 3), "hold": hold, "trimmed": True}
    timings[bid] = final
    beat["actual_duration_s"] = final
    print(f"{bid}: speech {speech:6.2f}s + hold {hold:.2f}s = {final:6.2f}s")

raw_path.write_text(json.dumps(raw, indent=2) + "\n")
timings_path.write_text(json.dumps(timings, indent=2) + "\n")
sheet_path.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
print(f"total {sum(timings[b['beat_id']] for b in sheet['beats']):.2f}s")
