"""Independent check of one watch-loop run (the finished-wrong-answer check).

It does not trust, or import, the agent. It reads the files a loop run left behind (the
loop report, the trace, each board's run report, raw response and prior state) with
the standard library only, recomputes what it can from the raw bytes, and compares the
result with the agent's report and with ``checks/expectations.toml``: what a person
knows about each company without the agent.

Usage::

    uv run python checks/check_watch.py data/watch/loops/<loop_id>

Exit status 0 when every check passes, 1 otherwise. Output is one Markdown table.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tomllib
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[1]
OK_BOARD = "OK"
ATTEMPTED = ("OK", "FAILED")


def _json(path: Path) -> Any:  # noqa: ANN401 - arbitrary JSON document
    return json.loads(path.read_text(encoding="utf-8"))


def _trace(loop_dir: Path) -> list[dict[str, Any]]:
    lines = (loop_dir / "trace.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines]


def _jobs(raw: Any) -> list[Any] | None:  # noqa: ANN401
    """The ``jobs`` list of a board response, or ``None`` if it is not a jobs object."""
    if not isinstance(raw, dict) or not isinstance(raw.get("jobs"), list):
        return None
    return list(raw["jobs"])


def check_board(
    board: dict[str, Any], trace: list[dict[str, Any]], expect: dict[str, Any]
) -> list[tuple[str, bool | None, str]]:
    """Checks one attempted board; returns ``(check, passed, detail)`` rows.

    ``passed`` is ``None`` for a fact recorded without a verdict.
    """
    rows: list[tuple[str, bool | None, str]] = []
    if board["run_folder"] is None:
        rows.append(("run saved", board["state"] != OK_BOARD, "the board raised"))
        return rows
    run_dir = PROJECT / board["run_folder"]
    run = _json(run_dir / "report.json")
    raw_ref = run.get("raw_evidence")
    results = [
        e
        for e in trace
        if e["event"] == "tool.fetch.result" and e["board"] == board["board"]
    ]
    if raw_ref is None:
        rows.append(("raw saved", board["state"] != OK_BOARD, "no raw response saved"))
        return rows
    body = (PROJECT / raw_ref["path"]).read_bytes()
    digest = hashlib.sha256(body).hexdigest()
    same = digest == raw_ref["sha256"] == (results[-1]["sha256"] if results else None)
    rows.append(("sha256 raw = report = trace", same, digest[:12]))
    try:
        jobs = _jobs(json.loads(body))
    except ValueError:
        jobs = None
    if jobs is None:
        claims = board["fetched_count"] is not None
        rows.append(("no count invented", not claims, "raw is not a jobs object"))
        return rows
    # Count every listed job, as the agent does; only jobs with an ID can be new.
    ids = {str(j["id"]) for j in jobs if isinstance(j, dict) and "id" in j}
    failed = board["state"] != OK_BOARD
    rows.append(
        (
            "count = raw jobs (a failed board may report none)",
            board["fetched_count"] == len(jobs)
            or (failed and board["fetched_count"] is None),
            f"raw {len(jobs)}, report {board['fetched_count']}",
        )
    )
    before = _json(run_dir / "state.before.json")
    if board["state"] == OK_BOARD and before is not None:
        new = len(ids - set(before["seen_ids"]))
        rows.append(
            ("new = raw - before", board["new_count"] == new, f"recomputed {new}")
        )
    company = expect.get(board["board"].split("/", 1)[1])
    if company is None:
        rows.append(("expected", False, "no expectation written for this company"))
        return rows
    system = board["board"].split("/", 1)[0]
    floor = company["min_postings"]
    system_ok = system == company["system"]
    floor_ok = len(jobs) >= floor
    system_detail = f"board {system}, careers page {company['system']}"
    floor_detail = f"{len(jobs)} vs {floor}"
    if not failed:
        rows.append(("careers page uses this system", system_ok, system_detail))
        rows.append(("at least the expected floor", floor_ok, floor_detail))
        return rows
    # A board the agent failed: the expectations are facts, and the decisive question
    # is whether the failure is justified (else the agent failed a good board).
    rows.append(("careers page uses this system", None, system_detail))
    rows.append(("at least the expected floor", None, floor_detail))
    rows.append(
        (
            "failed board misses an expectation",
            not (system_ok and floor_ok),
            "the agent failed it; "
            + (
                "justified"
                if not (system_ok and floor_ok)
                else "it meets every expectation"
            ),
        )
    )
    return rows


def check_loop(
    loop_dir: Path, expectations: Path
) -> list[tuple[str, str, bool | None, str]]:
    """Every check for one loop run, as ``(board, check, passed, detail)`` rows."""
    report = _json(loop_dir / "report.json")
    trace = _trace(loop_dir)
    expect = tomllib.loads(expectations.read_text(encoding="utf-8"))["companies"]
    rows: list[tuple[str, str, bool | None, str]] = []
    planned = trace[0]["planned"]
    reported = [b["board"] for b in report["boards"]]
    rows.append(
        (
            "(loop)",
            "every planned board reported",
            len(planned) == len(reported),
            f"{len(planned)} planned, {len(reported)} reported",
        )
    )
    attempts = sum(e["event"] == "tool.fetch.attempt" for e in trace)
    rows.append(
        (
            "(loop)",
            "requests = trace attempts <= budget",
            attempts == report["requests_used"] <= report["budget"]["max_requests"],
            f"{attempts} attempts",
        )
    )
    board_rows: list[tuple[str, str, bool | None, str]] = []
    for board in report["boards"]:
        if board["state"] in ATTEMPTED:
            for check, passed, detail in check_board(board, trace, expect):
                board_rows.append((board["board"], check, passed, detail))
    all_ok = all(b["state"] in (OK_BOARD, "SKIPPED_REPEAT") for b in report["boards"])
    checks_ok = all(passed is not False for _, _, passed, _ in board_rows)
    finished = report["exit"] == "FINISHED"
    rows.append(
        (
            "(loop)",
            "FINISHED only if every board is OK and checks out",
            not finished or (all_ok and checks_ok),
            f"agent says {report['exit']}",
        )
    )
    return rows + board_rows


def main(argv: list[str] | None = None) -> int:
    """Prints the table; returns 0 only if every check passes."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("loop_dir", type=Path)
    parser.add_argument(
        "--expectations", type=Path, default=PROJECT / "checks" / "expectations.toml"
    )
    args = parser.parse_args(argv)
    rows = check_loop(args.loop_dir, args.expectations)
    print(f"Independent check of {args.loop_dir.as_posix()}\n")
    print("| board | check | result | detail |")
    print("|---|---|---|---|")
    labels = {True: "PASS", False: "FAIL", None: "fact"}
    for board, check, passed, detail in rows:
        print(f"| {board} | {check} | {labels[passed]} | {detail} |")
    failed = sum(passed is False for _, _, passed, _ in rows)
    passed_count = sum(passed is True for _, _, passed, _ in rows)
    print(f"\n{passed_count} passed, {failed} failed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
