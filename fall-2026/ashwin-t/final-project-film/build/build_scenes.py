"""scenes.py = show-tell iso_kit.py (pasted, as the skill requires) + scene_body.py."""
import os
from pathlib import Path

R = Path(__file__).resolve().parent
# Where the Brutalist toolkit is checked out. Override with ART_HOME on another machine;
# the default is where mine lives, so this script is not portable without it.
ART = Path(os.environ.get("ART_HOME", Path.home() / "Desktop/College/CSYE7375/brutalist-final"))
KIT = ART / "skills/make/show-tell/templates/iso_kit.py"
if not KIT.exists():
    raise SystemExit(f"iso_kit.py not found at {KIT}\n"
                     f"Set ART_HOME to your brutalist.art checkout (commit b21f625).")
(R / "scenes.py").write_text(KIT.read_text() + "\n\n" + (R / "scene_body.py").read_text())
print("scenes.py written")
