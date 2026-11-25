#!/usr/bin/env python3
"""final_checks.py — checks on the verified master beyond the toolkit's gates (reused 2026-11-23 for the
Final Project Film; first written 2026-10-25). Writes into checks/:
  probe.txt            ffprobe streams + frame count, loudness (ebur128), silences >= 0.6 s, full decode
  beat_spans.json      [beat, start_s, dur_s] from each beat's render_duration_s
  frames-1..3.png      every beat at 15 / 50 / 90 %
  transitions.png      0.06 s either side of every cut
  whisper-master.txt   faster-whisper small.en transcript of the master (machine, not a human listen)
  bookend_check.txt    the toolkit's bookend_check.py (fails by design on the outro handle)
Run from this folder with the brutalist-daythread env on PATH.
"""
import json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
MASTER = HERE / "exports" / "daythread-final-project-film.mp4"
OUT = HERE / "checks"
TOOLKIT = HERE.parents[3] / "brutalist.art"
FONT = ImageFont.load_default(size=26)


def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def frame(t, w=960):
    rc, _ = sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(MASTER), "-frames:v", "1",
                "-vf", f"scale={w}:-1", str(OUT / "_f.png")])
    return Image.open(OUT / "_f.png").convert("RGB")


def sheet(items, path, cols=3):
    w, h = items[0][1].size
    rows = (len(items) + cols - 1) // cols
    img = Image.new("RGB", (cols * w, rows * (h + 34)), "white")
    d = ImageDraw.Draw(img)
    for i, (label, im) in enumerate(items):
        x, y = (i % cols) * w, (i // cols) * (h + 34)
        d.text((x + 6, y + 2), label, fill="black", font=FONT)
        img.paste(im, (x, y + 34))
    img.save(path)


def main():
    OUT.mkdir(exist_ok=True)
    sheet_beats = json.loads((HERE / "beat_sheet.json").read_text())["beats"]

    probe = []
    _, s = sh(["ffprobe", "-v", "error", "-show_entries",
               "format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate,pix_fmt,sample_rate,channels,nb_frames",
               "-of", "default=nw=1", str(MASTER)])
    probe += ["## ffprobe", s.strip()]
    _, s = sh(["ffmpeg", "-nostats", "-i", str(MASTER), "-af", "ebur128=framelog=quiet", "-f", "null", "-"])
    probe += ["", "## loudness (ebur128 summary)", s[s.rfind("Summary:"):].strip()]
    _, s = sh(["ffmpeg", "-nostats", "-i", str(MASTER), "-af", "silencedetect=noise=-50dB:d=0.6", "-f", "null", "-"])
    probe += ["", "## silences >= 0.6 s at -50 dB", "\n".join(l.split("] ")[-1] for l in s.splitlines() if "silence_" in l)]
    rc, s = sh(["ffmpeg", "-v", "error", "-i", str(MASTER), "-f", "null", "-"])
    probe += ["", "## full decode", f"exit {rc}; errors: {s.strip() or 'none'}"]
    (OUT / "probe.txt").write_text("\n".join(probe) + "\n")

    t, spans = 0.0, []
    for b in sheet_beats:
        spans.append([b["beat_id"], round(t, 4), b["render_duration_s"]])
        t += b["render_duration_s"]
    (OUT / "beat_spans.json").write_text(json.dumps(spans) + "\n")

    items = [(f"{bid} {int(p*100)}%  t={st + dur*p:.2f}s", frame(st + dur * p)) for bid, st, dur in spans for p in (0.15, 0.5, 0.9)]
    for i in range(3):
        sheet(items[i * 18:(i + 1) * 18], OUT / f"frames-{i + 1}.png")
    cuts = []
    for (a, sa, da), (b, sb, _) in zip(spans, spans[1:]):
        cuts += [(f"{a} end  t={sb - 0.06:.2f}s", frame(sb - 0.06, 640)), (f"{b} start  t={sb + 0.06:.2f}s", frame(sb + 0.06, 640))]
    sheet(cuts, OUT / "transitions.png", cols=4)
    (OUT / "_f.png").unlink()

    from faster_whisper import WhisperModel
    segs, _ = WhisperModel("small.en", device="cpu", compute_type="int8").transcribe(str(MASTER))
    lines = [f"faster-whisper small.en transcript of exports/{MASTER.name} (machine transcript, not a human listen)"]
    lines += [f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}" for s in segs]
    (OUT / "whisper-master.txt").write_text("\n".join(lines) + "\n")

    rc, s = sh(["python", str(TOOLKIT / "runtime" / "scripts" / "bookend_check.py"), str(HERE)])
    (OUT / "bookend_check.txt").write_text(s.strip() + f"\nbookend_check exit={rc}\n")
    print(f"master {t:.3f} s of beats; checks written to {OUT}")


if __name__ == "__main__":
    main()
