"""The independent check: it reads only the saved raw responses, never the agent's own counts, and compares.

For every board the report calls "checked", the last saved response must be a real job list whose size and new IDs
match the report. The boards in the report must be the boards in config/boards.json, and a run that says `finished`
may not have a failed or missing board. New IDs are recomputed from the raw files of earlier runs, not from the
agent's state file, and a board that answers with 0 jobs after having jobs before is flagged, not trusted.
Every file is opened through the permission policy's read check.
"""
import json
from pathlib import Path

from . import ats
from .policy import Policy


def _raw_ids(policy, path, system):
    return [j["id"] for j in ats.parse(system, policy.check_read(path).read_bytes())]


def earlier_ids(policy, raw_dir, stamp, system, name):
    """Every job ID this board showed in a saved response from an earlier real run (from the raw files alone)."""
    ids = set()
    for path in sorted(Path(raw_dir).glob(f"*-{system}-{name}-a*.json")):
        if path.name[:16] < stamp[:16] and "WRONG" not in path.name:
            try:
                ids |= set(_raw_ids(policy, path, system))
            except ats.BadData:
                pass
    return ids


def board_list_problems(report, configured):
    """The report must cover the configured boards in order; a run that stopped early may stop short, never add one."""
    reported = [b["board"] for b in report["boards"]]
    expected = [f"{b['system']}:{b['name']}" for b in configured]
    stopped_early = report["status"] in ("budget-exhausted", "error")
    if reported == expected or (stopped_early and reported == expected[:len(reported)]):
        return []
    missing = [b for b in expected if b not in reported]
    extra = [b for b in reported if b not in expected]
    return [f"the boards in the report do not match config/boards.json (missing: {missing or 'none'}; extra: {extra or 'none'})"]


def check(run_dir, root, policy=None):
    """Returns (problems, notes). No problems means the report matches the evidence; notes say what was not checked."""
    run_dir, root = Path(run_dir), Path(root)
    policy = policy or Policy(root=root, hosts=[])
    report = json.loads(policy.check_read(run_dir / "report.json").read_text(encoding="utf-8"))
    configured = json.loads(policy.check_read(root / "config" / "boards.json").read_text(encoding="utf-8"))
    stamp = run_dir.name[:16]
    problems, notes = board_list_problems(report, configured), []
    if report["status"] == "finished":
        problems += [f"{b['board']}: the run ended `finished`, but this board {b['result']} ({b['reason']})"
                     for b in report["boards"] if b["result"] != "checked"]
    for b in report["boards"]:
        system, name = b["board"].split(":", 1)
        if b["result"] != "checked":
            continue
        last = b["attempts"][-1] if b["attempts"] else None
        if not last or not last.get("raw"):
            problems.append(f"{b['board']}: reported as checked, but no response body was saved")
            continue
        try:
            ids = _raw_ids(policy, root / last["raw"], system)
        except ats.BadData as e:
            problems.append(f"{b['board']}: reported as checked with {b['jobs']} jobs, but the saved response "
                            f"({last['raw']}, {last['outcome']}) is not a job list: {e}")
            continue
        if len(ids) != b["jobs"]:
            problems.append(f"{b['board']}: report says {b['jobs']} jobs, the saved response has {len(ids)}")
        before = earlier_ids(policy, root / "evidence" / "raw", stamp, system, name)
        if not ids and before:
            problems.append(f"{b['board']}: the saved response has 0 jobs, but earlier saved responses had {len(before)}; "
                            f"an empty answer is not taken as \"no new jobs\" without a look")
            continue
        if not before:
            notes.append(f"{b['board']}: new IDs not recomputed (no earlier raw file in evidence/raw/)")
            continue
        expected_new = sorted(set(ids) - before)
        if sorted(b["new_ids"]) != expected_new:
            problems.append(f"{b['board']}: report says {len(b['new_ids'])} new, the raw files say {len(expected_new)}")
    if report["status"] == "finished" and problems:
        problems.insert(0, "the run ended `finished`, but its report does not match its own evidence")
    return problems, notes
