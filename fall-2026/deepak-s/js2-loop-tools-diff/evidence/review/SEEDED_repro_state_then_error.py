# SEEDED repro: the summary.json write fails after the state replace. Fake transport, temp folder.
import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1] + "/tests/js2"); sys.path.insert(0, sys.argv[1])
import js2kit
from jobwatch import tools as T
w = Path(tempfile.mkdtemp()); js2kit.setup_workdir(w, js2kit.THREE); os.chdir(w)
real = T.Tools.write_file
def failing(self, path, data, approval=None, mode="replace"):
    if str(path).endswith("summary.json"): raise OSError("SEEDED: disk full")
    return real(self, path, data, approval, mode)
T.Tools.write_file = failing
code = js2kit.run_loop(js2kit.SeededTransport(js2kit.three_ok_routes()))
rd = js2kit.run_dir(w)
print("exit", code, "| state/seen.json exists:", (w / "state" / "seen.json").exists(), "| summary.json exists:", (rd / "summary.json").exists())
