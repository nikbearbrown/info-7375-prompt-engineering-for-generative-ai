#!/usr/bin/env python3
"""make_e1.py: media/B01.png (script beat E1) for CueGate film 2.

Starts from the pitch film's B00 still (media/B01.base.png, a byte-for-byte copy of
youtube/cuegate-pitch/media/B00.png: Deepak's real claude.ai screenshot of 2026-10-14, unaltered and
scaled only, with its date caption). Adds two labels on the cream margin, outside the screenshot:
the act chip "1 · WHAT AND WHY" (top right) and the speaker tag "DEEPAK" (top left). Nothing inside
the screenshot is touched.
"""
import hashlib
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
BASE = HERE / "media" / "B01.base.png"
BASE_SHA = "1030efd2c025159db086a7fad84c4eea7e7344f988a3b9da3e5cc6d943e1d17e"   # pitch film media/B00.png
FONTS = Path(__import__("os").environ.get("ART_HOME") or HERE.parent.parent / "brutalist.art") / "runtime" / "fonts" / "EB_Garamond" / "static"
OUT = HERE / "media" / "B01.png"
INK = (0x3D, 0x39, 0x29)

if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA:
    raise SystemExit("make_e1.py: media/B01.base.png is not the pitch film's B00 still")
im = Image.open(BASE).convert("RGB")
d = ImageDraw.Draw(im)
bold = ImageFont.truetype(str(FONTS / "EBGaramond-Medium.ttf"), 64)
d.text((300, 200), "DEEPAK", font=bold, fill=INK)
chip = "1 · WHAT AND WHY"
w = d.textlength(chip, font=bold)
d.text((3840 - 300 - w, 200), chip, font=bold, fill=INK)
im.save(OUT)
(OUT.with_suffix(".source.txt")).write_text(
    "B01 still (script beat E1): the pitch film's B00 still (Deepak Kumaran T S's own screenshot of a Claude "
    "exchange on 2026-10-14, unaltered and scaled only, with its date caption), plus the act chip "
    "'1 · WHAT AND WHY' and the speaker tag 'DEEPAK' on the cream margin, added by make_e1.py. source: own. Not generated.\n")
print(OUT, im.size)
