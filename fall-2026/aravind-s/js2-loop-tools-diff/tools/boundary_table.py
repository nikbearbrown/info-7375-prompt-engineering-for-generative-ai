"""Fill BOUNDARY-TESTS.md's Actual and Match columns by running the 19 boundary cases.

The cases are the ones in tests/test_boundary.py, run the same way: requests through the real
network door with a stand-in opener (no network), files through the permission policy on a
temporary repo. My predictions in the table are never changed; only Actual and Match are written,
plus a section that quotes what the program said for each case.

Usage (from the repo root):  python3 tools/boundary_table.py [--check]
--check changes nothing and exits 1 when the table's Actual column differs from a fresh run.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TABLE = REPO / "BOUNDARY-TESTS.md"
DETAILS = "## What the program said"
sys.path.insert(0, str(REPO))

spec = importlib.util.spec_from_file_location("test_boundary", REPO / "tests" / "test_boundary.py")
cases = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cases)
SUMMARY = re.compile(r"^\d+ of \d+ predictions match\. .*\n?", re.MULTILINE)  # an earlier fill's summary
ROW = re.compile(r"^\|\s*(?P<n>\d+)\s*\|\s*(?P<action>.*?)\s*\|\s*(?P<predicted>allow|refuse|approval)\s*\|"
                 r"\s*(?P<actual>[^|]*?)\s*\|\s*(?P<match>[^|]*?)\s*\|$")


def run_cases() -> dict:
    box = cases.Sandbox()
    try:
        return {n: cases.outcome(call, box.root) for n, (_, call) in cases.actions(box).items()}
    finally:
        box.cleanup()


def filled(text: str, results: dict) -> str:
    lines, seen = [], set()
    for line in text.splitlines():
        match = ROW.match(line)
        if match:
            n = int(match.group("n"))
            word = results[n][0]
            agrees = "yes" if word == match.group("predicted") else "**no**"
            line = f"| {n} | {match.group('action')} | {match.group('predicted')} | {word} | {agrees} |"
            seen.add(n)
        lines.append(line)
    if seen != set(results):
        raise SystemExit(f"the table has rows for {sorted(seen)}, the cases are {sorted(results)}")
    body = "\n".join(lines)
    body = SUMMARY.sub("", body.split("\n" + DETAILS)[0]).rstrip() + "\n"
    matched = sum(1 for n in results if f"| {n} |" in body and "| yes |" in _row(body, n))
    body += (f"\n{matched} of {len(results)} predictions match. The Actual column and the section below come from "
             "`python3 tools/boundary_table.py`, which runs the same cases as `tests/test_boundary.py`; "
             "`--check` reruns them and compares.\n")
    body += f"\n{DETAILS}\n\n"
    for n in sorted(results):
        body += f"{n}. **{results[n][0]}**: {results[n][1]}\n"
    return body


def _row(body: str, n: int) -> str:
    return next(line for line in body.splitlines() if line.startswith(f"| {n} |"))


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    text = TABLE.read_text(encoding="utf-8")
    new = filled(text, run_cases())
    if args == ["--check"]:
        same = [line for line in new.splitlines() if ROW.match(line)] == \
               [line for line in text.splitlines() if ROW.match(line)]
        print("the table matches a fresh run" if same else "the table differs from a fresh run")
        return 0 if same else 1
    TABLE.write_text(new, encoding="utf-8")
    print(f"wrote {TABLE.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
