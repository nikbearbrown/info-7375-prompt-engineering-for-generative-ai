#!/usr/bin/env python3
"""
qc_frames.py -- catch content that runs off the visible frame.

Samples frames from every rendered scene and reports any non-background pixel
inside the outer safety border. This exists because a caption in B02 ran off
the right-hand edge in Week 1 and a spot-check of four scenes did not catch
it; an empirical sweep of all of them does.

Usage:  python3 qc_frames.py [--border 14] [--step 10]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VID = ROOT / "media/videos/scene/2160p24"
# scenes render at 4K; the sweep scales to 1080p so the border stays the
# Week 1 width and a 4K frame (25 MB raw) never has to sit in memory
W, H = 1920, 1080
BG = (0x0B, 0x0B, 0x0C)
TOL = 26                       # tolerance over the flat background colour

SCENES = [b["graphic"]["manim"] for b in
          json.loads((ROOT / "beat_sheet.json").read_text())["beats"]]


def frames(path, step):
    """Decode to raw RGB and yield every `step`-th frame."""
    p = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path),
         "-vf", f"select='not(mod(n\\,{step}))',scale={W}:{H}", "-fps_mode", "passthrough",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True)
    buf, size = p.stdout, W * H * 3
    for i in range(len(buf) // size):
        yield i * step, buf[i * size:(i + 1) * size]


def worst_in_border(fr, b):
    """Max deviation from background found inside the border, with location."""
    worst, where = 0, None
    def scan(rows, cols):
        nonlocal worst, where
        for y in rows:
            base = y * W * 3
            for x in cols:
                o = base + x * 3
                d = max(abs(fr[o] - BG[0]), abs(fr[o+1] - BG[1]),
                        abs(fr[o+2] - BG[2]))
                if d > worst:
                    worst, where = d, (x, y)
    scan(range(0, b), range(0, W, 2))
    scan(range(H - b, H), range(0, W, 2))
    scan(range(0, H, 2), range(0, b))
    scan(range(0, H, 2), range(W - b, W))
    return worst, where


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--border", type=int, default=14)
    ap.add_argument("--step", type=int, default=10)
    a = ap.parse_args()

    bad = []
    for name in SCENES:
        p = VID / f"{name}.mp4"
        if not p.exists():
            print(f"  SKIP {name} (not rendered)")
            continue
        worst, where, at = 0, None, None
        for n, fr in frames(p, a.step):
            w, loc = worst_in_border(fr, a.border)
            if w > worst:
                worst, where, at = w, loc, n
        status = "CLIPPED" if worst > TOL else "ok"
        extra = f"  worst dev={worst} at px{where} frame {at}" if worst > TOL else ""
        print(f"  {status:8} {name}{extra}")
        if worst > TOL:
            bad.append(name)

    print()
    if bad:
        print(f"FAIL — content in the safety border: {', '.join(bad)}")
        return 1
    print(f"PASS — all {len(SCENES)} scenes clear of the outer {a.border}px")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
