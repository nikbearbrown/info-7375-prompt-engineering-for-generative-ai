#!/usr/bin/env python3
"""
build_mux.py -- INFO 7375 Final Project Pitch Film (Swathi Baba Eswarappa)

Pairs each rendered Manim scene with its Kokoro narration beat, inserts a
short black gap between beats so the cuts breathe, and concatenates into the
final master.

Because every scene was rendered to its own narration length (scene.py locks
each scene with Beat.lock()), the A/V pairing here is 1:1 with no stretching
and no drift.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VID = ROOT / "media/videos/scene/2160p24"
MP3 = ROOT / "mp3"
WORK = ROOT / "build/segments"

# beat order and scene names come from the beat sheet, so the two cannot drift
SHEET = json.loads((ROOT / "beat_sheet.json").read_text())
SCENES = [(b["beat_id"], b["graphic"]["manim"]) for b in SHEET["beats"]]

# the toolkit's GATE MASTER spec: 3840x2160, 24 fps, h264, yuv420p
FPS, W, H, SR = 24, 3840, 2160, 48000


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("FFMPEG FAILED\n%s\n%s" % (" ".join(map(str, cmd)), r.stderr[-2500:]))
    return r


def dur(p):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", str(p)])
    return float(r.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gap", type=float, default=0.30)
    ap.add_argument("--out", default="BabaEswarappa_Swathi_INFO7375_FinalProjectFilm.mp4")
    # -19 sits inside the toolkit GATE LOUDNESS window (-28..-18 LUFS)
    ap.add_argument("--lufs", type=float, default=-19.0)
    a = ap.parse_args()

    # delete the previous master first: if the render set is incomplete this
    # run must fail loudly rather than leave yesterday's file to be packaged
    out_early = ROOT / a.out
    if out_early.exists():
        out_early.unlink()

    WORK.mkdir(parents=True, exist_ok=True)
    for f in WORK.glob("*.mp4"):
        f.unlink()

    timings = json.loads((MP3 / "timings.json").read_text())
    parts, total = [], 0.0

    # black spacer, built once, reused between beats
    gap = WORK / "gap.mp4"
    run(["ffmpeg", "-y", "-v", "error",
         "-f", "lavfi", "-i", f"color=c=0x0B0B0C:s={W}x{H}:r={FPS}:d={a.gap}",
         "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo:d={a.gap}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(gap)])

    print(f"{'beat':5} {'video':>8} {'audio':>8} {'seg':>8}")
    for i, (bid, scene) in enumerate(SCENES):
        v, au = VID / f"{scene}.mp4", MP3 / f"beat-{bid}.mp3"
        for p in (v, au):
            if not p.exists():
                sys.exit(f"missing: {p}")
        seg = WORK / f"seg_{bid}.mp4"
        # -shortest trims to whichever ends first; they differ by <0.02s.
        run(["ffmpeg", "-y", "-v", "error", "-i", str(v), "-i", str(au),
             "-map", "0:v:0", "-map", "1:a:0",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", "-r", str(FPS),
             "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-ac", "2",
             "-shortest", str(seg)])
        d = dur(seg)
        print(f"{bid:5} {dur(v):8.2f} {timings[bid]:8.2f} {d:8.2f}")
        parts.append(seg)
        total += d
        if i < len(SCENES) - 1:
            parts.append(gap)
            total += a.gap

    lst = WORK / "concat.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    out = ROOT / a.out
    raw = WORK / "concat_raw.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(lst), "-c", "copy", str(raw)])

    # two-pass EBU R128 loudness normalisation of the whole master; Kokoro
    # comes out near -24 LUFS, quiet for web playback. Video is copied as is.
    spec = f"I={a.lufs}:TP=-1.5:LRA=11"
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(raw), "-map", "0:a",
             "-af", f"loudnorm={spec}:print_format=json", "-f", "null", "-"])
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    norm = (f"loudnorm={spec}:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
            f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
            f":offset={m['target_offset']}:linear=true")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-map", "0:v", "-map", "0:a",
         "-c:v", "copy", "-af", norm, "-ar", str(SR),
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
    print(f"loudness   : {m['input_i']} LUFS -> target {a.lufs} LUFS")

    d = dur(out)
    print(f"\n{out.name}")
    print(f"  duration : {int(d//60)}:{d%60:05.2f}  ({d:.2f}s)")
    print(f"  expected : {total:.2f}s")
    print(f"  size     : {out.stat().st_size/1e6:.1f} MB")
    ok = 120 <= d <= 240
    print(f"  2-4 min  : {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
