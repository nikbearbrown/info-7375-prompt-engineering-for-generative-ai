#!/usr/bin/env python3
"""boost_audio.py: raise every narration mp3 by 3 dB, with a peak limiter, after Kokoro and before `art run`.

v3 measured -22.3 LUFS. +3 dB brings the film to about -19 LUFS, inside the toolkit's loudness window
(-28 to -18 LUFS, true peak at most -1 dBTP; runtime/scripts/loudness_check.py). The limiter holds
peaks under -2.5 dBFS. Sample count, sample rate and encoder settings stay the same, so durations
do not change.

Safe to run twice: mp3/boosted.json records the sha256 of each boosted file, and those are skipped.
"""
import hashlib, json, os, shutil, subprocess, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
MP3 = HERE / "mp3"
LOG = MP3 / "boosted.json"
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FILTER = "volume=3dB,alimiter=limit=0.75:level=false:latency=true"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def duration(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout)


done = json.loads(LOG.read_text()) if LOG.exists() else {}
for mp3 in sorted(MP3.glob("beat-*.mp3")):
    if done.get(mp3.name) == sha(mp3):
        print(f"{mp3.name}: already boosted")
        continue
    before = duration(mp3)
    with tempfile.TemporaryDirectory(dir=MP3) as tmp:
        wav, enc = Path(tmp) / "a.wav", Path(tmp) / "a.mp3"
        subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(mp3), "-af", FILTER, "-c:a", "pcm_s16le", str(wav)], check=True)
        subprocess.run([FFMPEG, "-y", "-v", "error", "-i", str(wav), "-c:a", "libmp3lame", "-q:a", "2", str(enc)], check=True)
        after = duration(enc)
        if abs(after - before) > 0.005:
            raise SystemExit(f"{mp3.name}: duration changed {before:.3f} -> {after:.3f}; not replaced")
        os.replace(enc, mp3)
    done[mp3.name] = sha(mp3)
    print(f"{mp3.name}: +3 dB, {after:.2f}s")
LOG.write_text(json.dumps(done, indent=2) + "\n")
