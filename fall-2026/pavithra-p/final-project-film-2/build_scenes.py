#!/usr/bin/env python3
"""build_scenes.py: write scenes.py = the toolkit's iso_kit.py + iso_originals_25.py + scenes_body.py.
Gate A copies only scenes.py, so the kit is pasted in rather than imported (show-tell SKILL.md)."""
import os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
KIT = Path(os.environ.get("ART_HOME", HERE.parent / "brutalist-showtell")) / "skills/make/show-tell/templates"
parts = [KIT / "iso_kit.py", KIT / "iso_originals_25.py", HERE / "scenes_body.py"]
out = "\n\n".join(p.read_text() for p in parts)
(HERE / "scenes.py").write_text(out)
print("scenes.py:", out.count("\n"), "lines from", ", ".join(p.name for p in parts))
