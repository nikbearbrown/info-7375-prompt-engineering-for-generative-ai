"""Reproduce the review-packet defect (found 2026-11-09, before any patch):
check_run.py reads the raw_path named in a run record WITHOUT asking the permission policy, so a
record pointing outside the assignment folder makes the check read a file the policy forbids, and
report "consistent" from it.

Usage (from js2-loop-tools-diff/):  python3 review/repro_check_reads_outside.py
Expected on the unpatched code:     "DEFECT: check read a file outside the folder"
"""
import datetime as dt
import json
import pathlib
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import check_run  # noqa: E402
from jobwatch2.policy import Policy  # noqa: E402

with tempfile.TemporaryDirectory() as d:
    d = pathlib.Path(d)
    root = d / "js2"
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns("runs", "__pycache__", "review"))
    run = root / "runs" / "r1"
    run.mkdir(parents=True)
    outside = d / "outside.json"  # NOT inside the assignment folder
    outside.write_text(json.dumps({"jobs": [{"id": i, "title": "X", "location": {"name": "US"},
                                             "offices": [{"name": "US"}],
                                             "first_published": "2026-11-08T00:00:00Z"} for i in range(5)]}))
    (run / "record.json").write_text(json.dumps({"exit": "finished", "boards": [
        {"key": "greenhouse/stripe", "ats": "greenhouse", "status": "ok", "fetched": 5, "raw_path": str(outside)}]}))
    print("policy decision for that read:", Policy(root).read(outside))
    try:
        rep = check_run.check(root, run, today=dt.date(2026, 11, 9))
    except PermissionError as e:
        print("OK: check refused the read:", e)
        sys.exit(0)
    print("check verdict:", rep["verdict"], "flags:", rep["flags"])
    print("DEFECT: check read a file outside the folder" if rep["verdict"] == "consistent" else "check flagged it")
    sys.exit(1)
