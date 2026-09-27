"""Typeset the math rows in beat_sheet.json (fills `src` and `aspect`): TypesetMath props rows and Manim `shot.math_rows`.

Usage:  python3 fill_math.py /path/to/brutalist.art
Uses the toolkit's own runtime/scripts/typeset_math.py (matplotlib mathtext, no LaTeX).
Safe to re-run: rows are regenerated from their `expression` every time.
"""
import json
import sys
from pathlib import Path

toolkit = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(toolkit / "runtime" / "scripts"))
from typeset_math import typeset  # noqa: E402

sheet_path = Path(__file__).resolve().parent / "beat_sheet.json"
sheet = json.loads(sheet_path.read_text())
count = 0
for beat in sheet["beats"]:
    shot = beat.get("shot") or {}
    rem = shot.get("remotion") or {}
    rows = list(rem["props"]["rows"]) if rem.get("pattern") == "TypesetMath" else []
    rows += shot.get("math_rows", [])          # Manim beats (scenes.py loads these as SVGMobject)
    for row in rows:
        done = typeset(row["expression"])
        row["src"], row["aspect"] = done["src"], done["aspect"]
        count += 1
sheet_path.write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
print(f"typeset {count} rows into {sheet_path.name}")
