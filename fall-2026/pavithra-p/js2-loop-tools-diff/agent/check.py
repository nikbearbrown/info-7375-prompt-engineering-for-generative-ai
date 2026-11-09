"""The independent check: it reads only the saved raw responses, never the agent's own counts, and compares.

For every board the report calls "checked", the last saved response must be a real job list whose size and new IDs
match the report. A run that says `finished` while any board's evidence is missing or is not a job list fails.
New IDs are recomputed from the raw files of earlier runs, not from the agent's state file.
"""
import json
from pathlib import Path

from . import ats


def _raw_ids(path, system):
    return [j["id"] for j in ats.parse(system, Path(path).read_bytes())]


def earlier_ids(raw_dir, stamp, system, name):
    """Every job ID this board showed in a saved response from an earlier real run (from the raw files alone)."""
    ids = set()
    for path in sorted(Path(raw_dir).glob(f"*-{system}-{name}-a*.json")):
        if path.name[:16] < stamp[:16] and "WRONG" not in path.name:
            try:
                ids |= set(_raw_ids(path, system))
            except ats.BadData:
                pass
    return ids


def check(run_dir, root):
    """Returns (problems, notes). No problems means the report matches the evidence; notes say what was not checked."""
    run_dir, root = Path(run_dir), Path(root)
    report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
    stamp = run_dir.name[:16]
    problems, notes = [], []
    for b in report["boards"]:
        system, name = b["board"].split(":", 1)
        if b["result"] != "checked":
            continue
        last = b["attempts"][-1] if b["attempts"] else None
        if not last or not last.get("raw"):
            problems.append(f"{b['board']}: reported as checked, but no response body was saved")
            continue
        try:
            ids = _raw_ids(root / last["raw"], system)
        except ats.BadData as e:
            problems.append(f"{b['board']}: reported as checked with {b['jobs']} jobs, but the saved response "
                            f"({last['raw']}, {last['outcome']}) is not a job list: {e}")
            continue
        if len(ids) != b["jobs"]:
            problems.append(f"{b['board']}: report says {b['jobs']} jobs, the saved response has {len(ids)}")
        before = earlier_ids(root / "evidence" / "raw", stamp, system, name)
        if not before:
            notes.append(f"{b['board']}: new IDs not recomputed (no earlier raw file in evidence/raw/)")
            continue
        expected_new = sorted(set(ids) - before)
        if sorted(b["new_ids"]) != expected_new:
            problems.append(f"{b['board']}: report says {len(b['new_ids'])} new, the raw files say {len(expected_new)}")
    if report["status"] == "finished" and problems:
        problems.insert(0, "the run ended `finished`, but its report does not match its own evidence")
    return problems, notes
