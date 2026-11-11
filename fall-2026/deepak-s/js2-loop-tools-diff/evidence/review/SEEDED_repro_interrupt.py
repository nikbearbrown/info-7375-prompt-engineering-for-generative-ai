# SEEDED repro: Ctrl-C (KeyboardInterrupt) during the second board's fetch. Fake transport, temp folder.
import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1] + "/tests/js2"); sys.path.insert(0, sys.argv[1])
import js2kit
w = Path(tempfile.mkdtemp()); js2kit.setup_workdir(w, js2kit.THREE); os.chdir(w)
t = js2kit.SeededTransport(js2kit.three_ok_routes())
real_open = t.open
def open_(req, timeout=None):
    if "lever" in req.full_url: raise KeyboardInterrupt
    return real_open(req, timeout)
t.open = open_
try:
    code = js2kit.run_loop(t)
    print("returned", code)
except BaseException as e:
    print("escaped:", type(e).__name__)
rd = js2kit.run_dir(w)
print("summary.json exists:", (rd / "summary.json").exists(), "| trace lines:", len((rd / "trace.jsonl").read_text().splitlines()))
