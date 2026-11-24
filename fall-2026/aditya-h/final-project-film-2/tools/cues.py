#!/usr/bin/env python3
"""tools/cues.py: word-level timings for every scene, so animations land on the spoken word.

For each scene, faster-whisper gives word start times from public/audio/<id>.wav; they're mapped onto the SCRIPT's words
(src/narration/<id>.txt) by position, so cue lookups use the real script text. Writes src/config/cues.json:
  { "<scene id>": [[word, start_seconds], ...] }
Scenes call at("<scene id>", "phrase") (src/components/cues.ts) to get the frame where that phrase is spoken.
Re-run after any narration change:  ~/brutalist.art/.venv/bin/python tools/cues.py
"""
import json, re
from pathlib import Path
from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[1]
model = WhisperModel("small.en", compute_type="int8")
out = {}
for s in json.loads((ROOT / "src/config/scenes.json").read_text()):
    wav, txt = ROOT / f"public/audio/{s['id']}.wav", ROOT / f"src/narration/{s['id']}.txt"
    words = txt.read_text().split()
    segs, _ = model.transcribe(str(wav), word_timestamps=True)
    heard = [w for seg in segs for w in seg.words]
    n_s, n_h = len(words), max(1, len(heard))
    out[s["id"]] = [[w, round(heard[min(n_h - 1, round(i * n_h / n_s))].start, 3) if heard else 0.0] for i, w in enumerate(words)]
    print(f"{s['id']}: {n_s} script words, {len(heard)} heard")
(ROOT / "src/config/cues.json").write_text(json.dumps(out) + "\n")
