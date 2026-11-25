"""Independent check (JS2 Step 7, R21): does each saved board response hold as many jobs as the
board itself says it has?

Why it exists: a board can answer 200 with well-formed JSON and a non-empty list that is still
missing postings. Every GATE check passes, the agent reports `finished`, and its own summary
can't show the gap, because the summary is built from the same short list. Greenhouse puts its
own count in `meta.total`, so comparing that with the list length catches it.

Why it is separate from the agent: the brief asks for a check that is not the agent's own report.
So this file imports nothing from job_agent and reads only the raw responses on disk; a TA can run
it on any run's evidence/raw/ folder and get the same answer.

Usage: python checks/total_check.py <raw folder or file> [...]
Exit status: 1 if any response's list is shorter or longer than its stated total, else 0.
"""

import json
import sys
from pathlib import Path

OK, MISMATCH, NO_TOTAL = "OK", "MISMATCH", "no total (can't check)"


def check_file(path: Path) -> tuple[str, int, int | None]:
    """(result, jobs in the list, total the board states). Ashby responses carry no total, so
    they are reported as not checkable instead of being passed: a silent pass would be a claim
    this check can't make."""
    body = json.loads(path.read_text())
    jobs = len(body.get("jobs", []))
    total = (body.get("meta") or {}).get("total")
    if total is None:
        return NO_TOTAL, jobs, None
    return (OK if total == jobs else MISMATCH), jobs, total


def response_files(target: Path) -> list[Path]:
    """Only the board bodies: a run folder also holds *.headers.txt and *_error.txt files, which
    have no job list to count."""
    if target.is_file():
        return [target]
    return sorted(p for p in target.rglob("*.json"))


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__.strip().splitlines()[-2], file=sys.stderr)
        return 2
    bad = 0
    print("| file | jobs in list | board's total | result |")
    print("|---|---|---|---|")
    for target in map(Path, argv):
        for f in response_files(target):
            result, jobs, total = check_file(f)
            bad += result == MISMATCH
            print(f"| {f} | {jobs} | {'—' if total is None else total} | {result} |")
    print(f"\n{bad} mismatch(es)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
