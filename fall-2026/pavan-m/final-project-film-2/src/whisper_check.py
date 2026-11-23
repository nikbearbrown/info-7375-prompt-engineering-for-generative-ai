#!/usr/bin/env python3
"""whisper_check.py — transcribe every beat MP3 and flag words Kokoro may have misread.

Run from the reel folder:  python3 whisper_check.py
Uses faster-whisper (installed by the toolkit). Downloads the small 'base.en' model once.
Audio is decoded with ffmpeg rather than PyAV: faster-whisper 1.2.1 passes an argument
(metadata_errors) that the installed PyAV 19 no longer accepts.
"""
import json, re, subprocess
import numpy as np
from pathlib import Path
from faster_whisper import WhisperModel

HERE = Path(__file__).resolve().parent
sheet = json.loads((HERE / "beat_sheet.json").read_text())
WATCH = ["Pavan", "Majji", "Postgres", "FastAPI", "Docker", "Datadog", "Bits", "SRE", "Microsoft",
         "Copilot", "seventy", "Claude", "Cite", "Line", "rollbacks", "config", "keyword", "engineer"]

def load(mp3):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32)

model = WhisperModel("base.en", device="cpu", compute_type="int8")
norm = lambda t: re.sub(r"[^a-z0-9 ]", " ", t.lower()).split()

for b in sheet["beats"]:
    bid = b["beat_id"]
    mp3 = HERE / "mp3" / f"beat-{bid}.mp3"
    if not mp3.exists():
        print(f"{bid}: MISSING {mp3.name}")
        continue
    segs, _ = model.transcribe(load(mp3), beam_size=5)
    heard = " ".join(s.text.strip() for s in segs)
    heard_words = set(norm(heard))
    missing = [w for w in WATCH if w.lower() in norm(b["narration_text"]) and w.lower() not in heard_words]
    flag = f"  <-- CHECK: {', '.join(missing)}" if missing else ""
    print(f"\n{bid}{flag}\n  script: {b['narration_text']}\n  heard : {heard}")
