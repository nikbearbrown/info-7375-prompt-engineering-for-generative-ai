#!/usr/bin/env python3
"""audio_post.py — after generate_audio_kokoro.py: pad BOUT with its 1.0 s silent tail (show-tell / OUTRO
rule), measure every beat with ffprobe, and store faster-whisper word timings per beat in beat_sheet.json
(`words`: [[word, start_s], …]) so scenes cue motions on the spoken word. No other beat is padded: the
measured narration sets the pacing (Aditya, 2026-10-14). Writes checks/whisper-beats.txt for the
pronunciation check. Re-runnable: BOUT's raw Kokoro file is kept in mp3/raw/.
"""
import json, shutil, subprocess
from pathlib import Path
from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]).decode())


sheet_p = HERE / "beat_sheet.json"
sheet = json.loads(sheet_p.read_text())
raw = HERE / "mp3" / "raw"; raw.mkdir(exist_ok=True)
model = WhisperModel("small.en", device="cpu", compute_type="int8")
(HERE / "checks").mkdir(exist_ok=True)
lines = ["faster-whisper small.en transcript per beat (machine transcript; not a human listen)", ""]
for b in sheet["beats"]:
    bid = b["beat_id"]
    out = HERE / "mp3" / f"beat-{bid}.mp3"
    src = raw / out.name
    if not src.exists():
        shutil.copy2(out, src)
    b["speech_s"] = round(dur(src), 3)
    if bid == "BOUT":
        tail = b.get("tail_silence_s", 1.0)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", f"apad=pad_dur={tail}",
                        "-c:a", "libmp3lame", "-q:a", "2", str(out)], check=True)
    else:
        shutil.copy2(src, out)
    b["audio_file"] = f"mp3/beat-{bid}.mp3"
    b["actual_duration_s"] = round(dur(out), 2)
    segs, _ = model.transcribe(str(src), word_timestamps=True)
    words = [[w.word.strip(), round(w.start, 2)] for s in segs for w in s.words]
    b["words"] = words
    heard = " ".join(w for w, _ in words)
    lines += [f"{bid}  ({b['actual_duration_s']} s)", f"  script: {b['narration_text']}", f"  heard:  {heard}", ""]
    print(bid, b["actual_duration_s"], "|", heard)
sheet_p.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
(HERE / "checks" / "whisper-beats.txt").write_text("\n".join(lines) + "\n")
print("total", round(sum(b["actual_duration_s"] for b in sheet["beats"]), 2), "s")
