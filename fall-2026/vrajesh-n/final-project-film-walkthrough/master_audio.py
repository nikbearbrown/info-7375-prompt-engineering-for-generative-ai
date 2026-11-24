"""master_audio.py - mix the narration beats with the sound effects into master_audio.wav (matches the toolkit's frame-rounded beat lengths)."""
import json, math, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
tl = json.loads((HERE / "timeline.json").read_text(encoding="utf-8"))
ids = sorted(tl["beats"]); bs = [tl["beats"][b]["bs"] for b in ids]; FPS = 30
tm = json.loads((HERE / "mp3" / "timings.json").read_text(encoding="utf-8"))
lens = [math.ceil(tm[b] * FPS - 1e-8) / FPS for b in ids]
eff = HERE.parent / "early-bird-walkthrough" / "out" / "effects.wav"
cmd = ["ffmpeg", "-y", "-v", "error"] + sum([["-i", str(HERE / "mp3" / f"beat-{b}.mp3")] for b in ids], []) + ["-i", str(eff)]
fl = []; n = len(ids)
for k, b in enumerate(ids):
    L = lens[k]
    fl.append(f"[{n}:a]atrim=start={bs[k]:.3f}:end={bs[k]+L:.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={L:.3f}[e{k}]")
    fl.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={L:.3f}[n{k}]")
    fl.append(f"[n{k}][e{k}]amix=inputs=2:normalize=0,atrim=0:{L:.3f}[m{k}]")
fl.append("".join(f"[m{k}]" for k in range(n)) + f"concat=n={n}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11[out]")
cmd += ["-filter_complex", ";".join(fl), "-map", "[out]", "-ar", "48000", "-ac", "2", str(HERE / "master_audio.wav")]
subprocess.run(cmd, check=True)
print("wrote master_audio.wav, expected", round(sum(lens), 3), "s")
