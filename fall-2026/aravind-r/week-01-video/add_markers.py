"""Burn section markers ("2 · Direct route", top-right of each beat) and per-beat stamps into a compiled cut.

Stamps: a beat may carry `stamp: {text, x, y, at_s}` (x, y = top-left as fractions of the frame; at_s =
seconds into the beat). B00 uses one for the date of the real Claude reply, which the toolkit's
composer component has no prop for.

Usage:  python3 add_markers.py <in.mp4> <out.mp4>
Run on the compiled cut (review or final). Labels come from each beat's `marker` field in
beat_sheet.json; beats without one (title card, outro) get none. Beat start times follow
compile.py's own clock: each beat lasts ceil(actual_duration_s * fps) / fps.
Why top-right: it is the one corner that is empty in every beat of this video.
"""
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"
FPS = 24
INK_SOFT = (110, 106, 87, 255)          # #6E6A57, the video's secondary text colour
FONT_NAMES = ["EBGaramond-Medium.ttf", "EBGaramond-Regular.ttf"]


def find_font():
    for d in [Path.home() / "Library/Fonts", Path.home() / ".local/share/fonts", Path("/Library/Fonts")]:
        for name in FONT_NAMES:
            if (d / name).exists():
                return str(d / name)
    raise SystemExit("EB Garamond not found; run the toolkit's ./setup --install (it installs the fonts)")


def main(src, dst):
    sheet = json.loads((HERE / "beat_sheet.json").read_text())
    h = int(subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=height",
                            "-of", "csv=p=0", src], capture_output=True, text=True, check=True).stdout.strip())
    w = round(h * 16 / 9)
    size = round(h * 0.03)                   # ≈ 32 px at 1080p
    right, top = round(w * 0.95), round(h * 0.05)   # title-safe corner (5 % inset)
    font = ImageFont.truetype(find_font(), size)

    t, overlays = 0.0, []
    tmp = Path(tempfile.mkdtemp(prefix="markers-"))

    def label_png(text, name, fnt):
        box = fnt.getbbox(text)
        img = Image.new("RGBA", (box[2] - box[0] + 4, box[3] - box[1] + 4), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((2 - box[0], 2 - box[1]), text, font=fnt, fill=INK_SOFT)
        png = tmp / f"{name}.png"
        img.save(png)
        return png, img.width

    for beat in sheet["beats"]:
        dur = math.ceil(float(beat["actual_duration_s"]) * FPS - 1e-8) / FPS
        if beat.get("marker"):
            png, iw = label_png(beat["marker"], beat["beat_id"], font)
            overlays.append((png, t, t + dur, right - iw, top))
        st = beat.get("stamp")
        if st and "x" in st:
            sfont = ImageFont.truetype(find_font(), round(h * st.get("size", 0.024)))
            png, _ = label_png(st["text"], beat["beat_id"] + "_stamp", sfont)
            overlays.append((png, t + float(st.get("at_s", 0)), t + dur, round(w * st["x"]), round(h * st["y"])))
        t += dur

    cmd = [FFMPEG, "-y", "-v", "error", "-i", src]
    for png, *_ in overlays:
        cmd += ["-loop", "1", "-framerate", str(FPS), "-i", str(png)]   # a stream, so the fade has frames to act on
    chain, prev = [], "0:v"
    for i, (_, a, b, x, y) in enumerate(overlays):
        # fade each marker in over 0.3 s so it doesn't pop
        chain.append(f"[{i + 1}:v]format=rgba,fade=in:st={a:.3f}:d=0.3:alpha=1[m{i}]")
        chain.append(f"[{prev}][m{i}]overlay={x}:{y}:shortest=1:enable='between(t,{a:.3f},{b - 0.001:.3f})'[v{i}]")
        prev = f"v{i}"
    cmd += ["-filter_complex", ";".join(chain), "-map", f"[{prev}]", "-map", "0:a",
            "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", dst]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp)
    print(f"{len(overlays)} markers → {dst}  (timeline {t:.2f}s)")


if __name__ == "__main__":
    main(*sys.argv[1:3])
