#!/usr/bin/env python3
"""qc_film.py — the Phase 4 measurements for the Readback project film (my own QC, beside the toolkit gates).

Usage: python3 qc_film.py <film.mp4>
Writes gates/QC.json, gates/contact-*.png (fps=1/4, tile=6x8) and gates/boundaries/*.png, and prints a summary.

Measures, on the delivered file:
  freeze    ffmpeg freezedetect=n=0.003:d=3 → every frozen span and the total, as a share of the runtime;
            the same at d=2.5 → every static hold longer than 2.5 s (each must be listed in SHOTLIST.md)
  black     blackdetect=d=0.1:pix_th=0.10 → any black span
  loudness  ebur128 (peak=true) → integrated LUFS and true peak
  dead air  silencedetect=noise=-50dB:d=1.2 on the audio → any silence of 1.2 s or more
  runtime   ffprobe duration against the 240 s cap
  cuts      the RGB of the last frame before and the first frame after every beat boundary, at four points each
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
film = sys.argv[1]
G = os.path.join(HERE, "gates")
os.makedirs(os.path.join(G, "boundaries"), exist_ok=True)
beats = json.load(open(os.path.join(HERE, "beat_sheet.json")))["beats"]


def ff(args):
    return subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *args], capture_output=True, text=True).stderr


def spans(log, kind):
    starts = [float(x) for x in re.findall(rf"{kind}_start: ?([\d.]+)", log)]
    ends = [float(x) for x in re.findall(rf"{kind}_end: ?([\d.]+)", log)]
    return [(s, e) for s, e in zip(starts, ends + [None] * (len(starts) - len(ends)))]


dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", film],
                           capture_output=True, text=True).stdout.strip())
out = {"file": os.path.basename(film), "duration_s": round(dur, 3)}

for d, key in ((3, "freeze_3s"), (2.5, "holds_2_5s")):
    log = ff(["-i", film, "-map", "0:v", "-vf", f"freezedetect=n=0.003:d={d}", "-f", "null", "-"])
    sp = [(s, e if e is not None else dur) for s, e in spans(log, "freeze")]
    out[key] = [{"start": round(s, 2), "end": round(e, 2), "dur": round(e - s, 2)} for s, e in sp]
out["freeze_total_s"] = round(sum(x["dur"] for x in out["freeze_3s"]), 2)
out["freeze_share"] = round(out["freeze_total_s"] / dur, 4)

log = ff(["-i", film, "-map", "0:v", "-vf", "blackdetect=d=0.1:pix_th=0.10", "-f", "null", "-"])
out["black"] = [{"start": s, "end": e} for s, e in spans(log, "black")]

log = ff(["-i", film, "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"])
summ = log[log.rfind("Summary:"):]
out["lufs_integrated"] = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
out["true_peak_dbtp"] = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", summ).group(1))

log = ff(["-i", film, "-map", "0:a", "-af", "silencedetect=noise=-50dB:d=1.2", "-f", "null", "-"])
out["silence_1_2s"] = [{"start": s, "end": e} for s, e in spans(log, "silence")]

# beat boundaries from the measured clip lengths (the compile concatenates clips at these lengths)
t, cuts = 0.0, []
for b in beats[:-1]:
    t += float(b["actual_duration_s"])
    cuts.append((b["beat_id"], round(t, 3)))
out["cuts"] = []
pts = [(8, 8), (8, 1072), (1912, 8), (1912, 1072)]
for bid, ct in cuts:
    row = {"after": bid, "t": ct}
    for side, ts in (("before", max(0, ct - 0.05)), ("after", ct + 0.05)):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ts:.3f}", "-i", film, "-frames:v", "1", "-f", "rawvideo",
                              "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        w = 1920
        row[side] = [list(raw[(y * w + x) * 3:(y * w + x) * 3 + 3]) for x, y in pts]
    out["cuts"].append(row)
colours = {tuple(c) for r in out["cuts"] for side in ("before", "after") for c in r[side]}
out["cut_colours"] = sorted(colours)

# section-boundary grabs: the frame just before and just after each part change, plus first and last frames
t, starts = 0.0, {}
for b in beats:
    starts.setdefault(b["act"], t)
    t += float(b["actual_duration_s"])
for part, ts in starts.items():
    for tag, at in (("before", max(0, ts - 0.05)), ("after", ts + 0.05)):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.3f}", "-i", film, "-frames:v", "1",
                        os.path.join(G, "boundaries", f"{int(ts):03d}s-{part}-{tag}.png")])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i", film, "-frames:v", "1",
                os.path.join(G, "boundaries", "last-frame.png")])
out["sections"] = {p: round(s, 2) for p, s in starts.items()}

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", film, "-vf", "fps=1/4,scale=480:-1,tile=6x8",
                os.path.join(G, "contact-%02d.png")])
json.dump(out, open(os.path.join(G, "QC.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k not in ("cuts", "holds_2_5s", "freeze_3s")}, indent=1))
print("freeze ≥3 s:", out["freeze_3s"])
print("holds ≥2.5 s:", out["holds_2_5s"])
