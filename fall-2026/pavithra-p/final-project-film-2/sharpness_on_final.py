"""Run the toolkit's own sharpness gate on the delivered film instead of the review cut.

sharpness_check.py takes only a reel folder and picks the review cut (mp4/<slug>-slate.mp4) itself. This loads
the same module unchanged and points its master lookup at exports/dryrun-project-film.mp4; the measurement, threshold
and report format are the toolkit's own.
"""
import importlib.util
import sys
from pathlib import Path

tool, reel = Path(sys.argv[1]), Path(sys.argv[2]).resolve()
spec = importlib.util.spec_from_file_location("sharpness_check", tool)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod._find_master = lambda reel_dir: reel_dir / "exports" / "dryrun-project-film.mp4"
sys.argv = [str(tool), str(reel)]
mod.main()
