"""Probe a case the B8 tests do not cover (review packet, 'one case your test would still miss').
Builds a disposable project whose runs/ folder is itself a symlink to a folder outside it."""
import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from jsa import policy

root = Path(tempfile.mkdtemp(prefix="js2-probe-"))
outside = Path(tempfile.mkdtemp(prefix="js2-elsewhere-"))
os.symlink(outside, root / "runs")
rid = "2026-11-10T00-00-00Z-probe"
try:
    p = policy.write_text(root, f"runs/{rid}/x.txt", "written", run_id=rid)
    print(f"ALLOWED: write landed at {p}")
    print(f"outside the project? {not p.is_relative_to(root.resolve())}")
except policy.PolicyError as e:
    print(f"REFUSED: {e}")
