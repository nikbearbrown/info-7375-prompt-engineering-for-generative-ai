"""Independent check of a finished run's claims against its saved raw responses.

Usage: .venv/bin/python tools/independent_check.py RUN_FILE [--base REPO_ROOT]

RUN_FILE is a JS2 trace (runs/js2/*.json) or a JS1 run record (runs/*.json).
This file deliberately imports nothing from either agent: it re-reads the raw bytes the run saved,
recounts the postings itself, and compares the run's claims with what the bytes show.
It never fetches anything. Exit 0 if every check passes, 1 if any fails.
"""
import argparse
import json
import pathlib
import sys

EXPECTED_EXIT = {"finished": 0, "incomplete": 10, "budget-exhausted": 11, "error": 12}


def _recount(raw_path):
    """Postings in a saved Greenhouse or Lever response, or None if the bytes are not a board."""
    try:
        data = json.loads(raw_path.read_bytes())
    except (OSError, ValueError):
        return None
    if isinstance(data, dict) and isinstance(data.get("jobs"), list):
        return len(data["jobs"])
    if isinstance(data, list):
        return len(data)
    return None


def _finding(check, passed, detail, board=None):
    return {"check": check, "board": board, "passed": bool(passed), "detail": detail}


def _resolve(base, path):
    path = pathlib.Path(path)
    return path if path.is_absolute() else base / path


def _check_js1(record, base):
    raw = _resolve(base, record["source"])
    count = _recount(raw)
    board = record.get("board")
    out = [_finding("count-matches-raw", count == record.get("postings_in_response"),
                    f"run says {record.get('postings_in_response')}; saved bytes hold {count}", board)]
    # JS1 writes a run record only for a run it completed, so any record is a success claim.
    empty_claim = count == 0 and record.get("new_count") == 0
    out.append(_finding("empty-response-claimed-as-no-new-jobs", not empty_claim,
                        "saved response holds 0 postings, yet the run completed and reported 0 new: "
                        "an empty response cannot show that there are no new jobs" if empty_claim
                        else f"saved response holds {count} postings", board))
    return out


def _check_js2(trace, base):
    out = []
    observed = [b.get("board") for b in trace.get("boards", [])]
    missing = [name for name in trace.get("selection", []) if name not in observed]
    out.append(_finding("every-selected-board-observed", not missing,
                        f"selected boards absent from the trace: {missing}" if missing
                        else f"all {len(observed)} selected boards appear"))
    status = trace.get("status")
    out.append(_finding("exit-code-matches-status", EXPECTED_EXIT.get(status) == trace.get("exit_code"),
                        f"status {status!r}, exit code {trace.get('exit_code')!r}"))
    not_ok = [b.get("board") for b in trace.get("boards", []) if b.get("outcome") != "ok"]
    if status == "finished":
        out.append(_finding("finished-means-every-board-ok", not not_ok and not missing,
                            f"finished, but these boards were not ok: {not_ok}" if not_ok
                            else "every board ok"))
    if trace.get("state_updated"):
        out.append(_finding("state-only-after-finished", status == "finished",
                            f"state_updated is true with status {status!r}"))
    for b in trace.get("boards", []):
        name = b.get("board")
        if b.get("outcome") != "ok":
            zeroed = b.get("postings_in_response") != "unknown" or b.get("new_count") != "unknown"
            out.append(_finding("failed-board-not-counted", not zeroed,
                                f"outcome {b.get('outcome')!r}; postings/new recorded as "
                                f"{b.get('postings_in_response')!r}/{b.get('new_count')!r} (must be 'unknown')",
                                name))
            continue
        raw_path = b.get("raw_path")
        raw = _resolve(base, raw_path) if raw_path else None
        if raw is None or not raw.is_file():
            out.append(_finding("raw-response-saved", False, f"ok board without a saved raw file: {raw_path}", name))
            continue
        count = _recount(raw)
        out.append(_finding("count-matches-raw", count == b.get("postings_in_response"),
                            f"trace says {b.get('postings_in_response')}; saved bytes hold {count}", name))
        out.append(_finding("empty-response-claimed-as-no-new-jobs", count != 0,
                            "saved response holds 0 postings but the board is reported ok" if count == 0
                            else f"saved response holds {count} postings", name))
    return out


def check_run(record_path, base_dir="."):
    record_path, base = pathlib.Path(record_path), pathlib.Path(base_dir)
    record = json.loads(record_path.read_text())
    return _check_js2(record, base) if "boards" in record else _check_js1(record, base)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_file")
    parser.add_argument("--base", default=str(pathlib.Path(__file__).resolve().parent.parent),
                        help="repository root that relative raw paths are resolved against")
    args = parser.parse_args(argv)
    findings = check_run(args.run_file, args.base)
    for f in findings:
        where = f" [{f['board']}]" if f["board"] else ""
        print(f"{'PASS' if f['passed'] else 'FAIL'}  {f['check']}{where}: {f['detail']}")
    failed = [f for f in findings if not f["passed"]]
    print(f"\n{len(findings) - len(failed)} passed, {len(failed)} failed — "
          + ("the run's claims are NOT supported by its saved responses" if failed
             else "the run's claims match its saved responses"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
