"""Independent check of a saved run (reads raw files, not the agent's report).

    python3 check.py out/runs/<id>/trace.json [--previous out/runs/<earlier>/trace.json ...]
Exit status 0 = no findings, 1 = findings.
"""

import argparse
import sys
from pathlib import Path

from jsagent2.check import check_run

ROOT = Path(__file__).resolve().parent


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("trace")
    ap.add_argument("--previous", nargs="*", default=[])
    ap.add_argument("--root", default=str(ROOT), help="folder the trace's raw_file paths are relative to")
    a = ap.parse_args(argv)
    findings = check_run(a.root, a.trace, a.previous)
    if not findings:
        print(f"independent check: {a.trace}: no findings")
        return 0
    print(f"independent check: {a.trace}: {len(findings)} finding(s)")
    for f in findings:
        print(f"  [{f['kind']}] {f['board']}: {f['detail']}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
