"""Independent check of one loop run (GATE.md section 5, "Intentional empty-board weakness").

Uses summary.json only to learn which raw file belongs to which board. Posting counts are
recomputed here from each saved raw response, with code that does not import the loop's
parser, so a wrong count or an empty board the loop accepted is caught from the evidence.

    python check_run.py out/runs/<stamp>
"""

import json
import sys
from pathlib import Path


def _count_postings(system, data):
    """Return the number of postings in a raw response, or raise ValueError if the shape is wrong."""
    if system == "lever":
        if not isinstance(data, list):
            raise ValueError("lever response is not a top-level list")
        return len(data)
    if system in ("greenhouse", "ashby"):
        if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
            raise ValueError(f"{system} response has no 'jobs' list")
        return len(data["jobs"])
    raise ValueError(f"unknown system {system!r}")


def check_run(run_dir):
    run_dir = Path(run_dir)
    try:
        summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
        boards = summary["boards"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        return [f"run: summary.json unreadable: {e}"]

    problems = []
    for key, b in boards.items():
        status = b.get("status")
        if status != "ok":
            if b.get("postings") is not None:
                problems.append(f"{key}: status {status} but a posting count ({b['postings']}) was reported")
            continue

        raw_rel = b.get("raw_file")
        if not raw_rel:
            problems.append(f"{key}: reported ok but no raw response is recorded")
            continue
        raw_path = (run_dir / raw_rel).resolve()
        if not raw_path.is_relative_to(run_dir.resolve()):
            problems.append(f"{key}: raw file path points outside the run folder: {raw_rel}")
            continue
        try:
            data = json.loads(raw_path.read_bytes())
            count = _count_postings(key.split(":", 1)[0], data)
        except (OSError, ValueError) as e:
            problems.append(f"{key}: reported ok but raw response {raw_rel} cannot be counted: {e}")
            continue

        if count == 0:
            problems.append(
                f"{key}: SUSPICIOUS empty board: raw response {raw_rel} has 0 postings, "
                f"but the loop marked the board ok (run status: {summary.get('status')})"
            )
        if b.get("postings") != count:
            problems.append(f"{key}: loop reported {b.get('postings')} postings, raw response has {count}")
    return problems


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: python check_run.py <run_dir>", file=sys.stderr)
        return 2
    problems = check_run(argv[0])
    for p in problems:
        print(f"PROBLEM  {p}")
    print(f"{len(problems)} problem(s) found in {argv[0]}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
