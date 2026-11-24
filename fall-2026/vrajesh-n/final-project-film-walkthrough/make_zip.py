"""make_zip.py - build Nasit_Vrajesh_INFO7375_FinalProjectFilm.zip from this reel folder (no caches, no private data, no raw clips)."""
import zipfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "Nasit_Vrajesh_INFO7375_FinalProjectFilm.zip"
INCLUDE = ["README.md", "BUILD-PROMPT.md", "SOURCES.md", "FRICTIONAL.md", "FACTCHECK.md", "SHOTLIST.md", "PROMPTS.md", "TYPECHECK.md",
           "beat_sheet.json", "timeline.json", "assemble.py", "port_engine.py", "master_audio.py", "make_zip.py"]
files = [HERE / f for f in INCLUDE if (HERE / f).is_file()]
files += sorted((HERE / "mp3").glob("beat-B*.mp3")) + [HERE / "mp3" / "timings.json"]
files += sorted((HERE / "_qc").glob("REPORT.md")) + sorted((HERE / "_qc").glob("contact_sheet.png"))
files += sorted((HERE / "final").glob("*.mp4"))
walk = HERE.parent / "early-bird-walkthrough"
for rel in ["cues.json", "make_sheet.py", "film.src.html", "render/render.js"]:
    if (walk / rel).is_file(): files.append(walk / rel)
files += sorted((walk / "icons").glob("*.svg"))
missing = [f for f in ("FRICTIONAL.md",) if not (HERE / f).is_file()]
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for f in files:
        z.write(f, f.relative_to(HERE.parent))
print("wrote", OUT, round(OUT.stat().st_size / 1e6, 1), "MB,", len(files), "files")
if missing: print("WARNING: missing", missing, "- write it before you submit")
