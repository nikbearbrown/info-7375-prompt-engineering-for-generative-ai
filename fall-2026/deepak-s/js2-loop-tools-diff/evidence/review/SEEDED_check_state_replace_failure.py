# SEEDED check (Claude Code, Claude Opus 5.5, 2026-11-10), run after patch 3a4c1fb. Not part of the test suite.
# The state/seen.json write raises OSError; every other write passes through. Fake transport, temp folder.
import json, os, sys, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1] + "/tests/js2"); sys.path.insert(0, sys.argv[1])
import js2kit
from jobwatch import tools as T
w = Path(tempfile.mkdtemp()); js2kit.setup_workdir(w, js2kit.THREE); os.chdir(w)
real = T.Tools.write_file
def failing(self, path, data, approval=None, mode="replace"):
    if str(path).endswith("state/seen.json"): raise OSError("SEEDED: state disk full")
    return real(self, path, data, approval, mode)
T.Tools.write_file = failing
code = js2kit.run_loop(js2kit.SeededTransport(js2kit.three_ok_routes()))
s = json.loads((js2kit.run_dir(w) / "summary.json").read_text())
md = (js2kit.run_dir(w) / "trace.md").read_text().splitlines()[2]
print("exit", code, "| state exists:", (w / "state" / "seen.json").exists(), "| summary exit:", s["exit"], s["exit_code"],
      "| state_updated:", s["state_updated"], "| needs_deepak:", s["needs_deepak"])
print("trace.md line 3:", md)
