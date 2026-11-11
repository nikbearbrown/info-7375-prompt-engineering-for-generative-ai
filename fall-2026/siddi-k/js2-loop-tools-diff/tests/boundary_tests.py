"""Boundary tests for the permission policy (GATE.md §5). Refuses to run until Siddi's predictions are filled in and
committed (BOUNDARY-PREDICTIONS.md), then writes BOUNDARY-TESTS.md: prediction next to the actual result.

    python tests/boundary_tests.py
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from harness import ROOT, temp_root  # noqa: E402

from agent2 import http, policy  # noqa: E402


def outcome(fn) -> str:
    try:
        fn()
        return "allowed"
    except policy.NeedsApproval as e:
        return f"needs approval ({e})"
    except policy.Refused as e:
        return f"refused ({e})"


def make_link(link: Path, target: Path) -> str:
    try:
        os.symlink(target, link, target_is_directory=True)
        return "symlink"
    except OSError:
        import _winapi                     # Windows without symlink privilege: a directory junction instead
        _winapi.CreateJunction(str(target), str(link))
        return "junction"


def cases(tmp: Path):
    outside = Path(tempfile.mkdtemp(prefix="js2outside")).resolve()
    kind = make_link(tmp / "evidence" / "runs" / "link", outside)
    (tmp / "evidence" / "runs" / "existing.json").write_text("{}", encoding="utf-8")
    cred = Path.home() / ".claude" / ".credentials.json"
    return [
        (1, lambda: policy.check_url("https://boards-api.greenhouse.io/v1/boards/stripe/jobs")),
        (2, lambda: policy.check_url("https://evil.example.com/jobs")),
        (3, lambda: policy.check_url("https://boards-api.greenhouse.io.evil.com/v1/boards/stripe/jobs")),
        (4, lambda: policy.check_url("http://boards-api.greenhouse.io/v1/boards/stripe/jobs")),
        (5, lambda: http._NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://stripe.com/jobs")),
        (6, lambda: policy.check_write("evidence/runs/2026-11-11T00-00-00Z/trace.jsonl")),
        (7, lambda: policy.check_write("evidence/runs/../GATE.md")),
        (8, lambda: policy.check_write("evidence/runs-evil/x.json")),
        (9, lambda: policy.check_write("evidence/runs/link/x.json")),
        (10, lambda: policy.check_write("evidence/runs/existing.json")),
        (11, lambda: policy.check_write("evidence/runs/existing.json", approved=True)),
        (12, lambda: policy.check_write("config/boards.json")),
        (13, lambda: policy.check_read("config/boards.json")),
        (14, lambda: policy.check_read(cred)),
        (15, lambda: policy.check_write(r"C:\Windows\Temp\x.json" if os.name == "nt" else "/tmp/x.json")),
    ], kind


def predictions() -> dict:
    rows = {}
    for line in (ROOT / "BOUNDARY-PREDICTIONS.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*(\d+)\s*\|(.*)\|(.*)\|\s*$", line)
        if m:
            rows[int(m.group(1))] = (m.group(2).strip(), m.group(3).strip())
    return rows


def committed() -> bool:
    rel = (ROOT / "BOUNDARY-PREDICTIONS.md").relative_to(ROOT)
    tracked = subprocess.run(["git", "log", "-1", "--format=%h", "--", str(rel)], cwd=ROOT, capture_output=True, text=True)
    dirty = subprocess.run(["git", "status", "--porcelain", "--", str(rel)], cwd=ROOT, capture_output=True, text=True)
    return bool(tracked.stdout.strip()) and not dirty.stdout.strip()


def main() -> int:
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8")
    pred = predictions()
    if len(pred) < 15 or any(not p for _, p in pred.values()) or not committed():
        print("refusing to run: fill every 'What should happen' cell in BOUNDARY-PREDICTIONS.md and commit it first")
        return 2
    with temp_root() as tmp:
        cs, kind = cases(tmp)
        results = [(n, outcome(fn)) for n, fn in cs]
    lines = ["# Boundary tests (GATE.md §5)", "",
             f"Run by `python tests/boundary_tests.py` against a throwaway copy of the folder layout. Case 9's link was a "
             f"**{kind}** on this machine. Predictions are Siddi's, committed before this ran "
             f"(`BOUNDARY-PREDICTIONS.md`).", "",
             "| # | Case | Siddi predicted | Actual (from the code) |", "|---|---|---|---|"]
    for n, actual in results:
        case, p = pred[n]
        lines.append(f"| {n} | {case} | {p} | {actual} |")
    (ROOT / "BOUNDARY-TESTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for n, actual in results:
        print(f"{n:2}  predicted: {pred[n][1][:40]:40}  actual: {actual[:90]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
