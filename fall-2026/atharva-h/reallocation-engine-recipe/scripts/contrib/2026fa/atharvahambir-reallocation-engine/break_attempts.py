#!/usr/bin/env python3
"""break_attempts.py — prove the offline tests can catch the bugs that matter. Exits 0 only if every mutant is caught.

    python3 scripts/contrib/2026fa/atharvahambir-reallocation-engine/break_attempts.py

1. Runs the offline suite against the real daily_check.py — it must pass.
2. For each mutant in fixtures/BROKEN-mutants.json: writes daily_check.py with that one edit into a
   temporary folder inside this one (the real file is never touched), runs the suite against it with
   DAILY_CHECK_SCRIPT pointing at the copy, and requires the suite to FAIL — naming the test that should catch it.
3. Removes the temporary copies and prints one line per mutant.

A mutant whose `find` text no longer appears exactly once is reported as stale, not silently skipped.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESTS = HERE / "test_daily_check.py"
SPEC = HERE / "fixtures" / "BROKEN-mutants.json"


def run_suite(script):
    env = dict(os.environ, DAILY_CHECK_OFFLINE="1", DAILY_CHECK_SCRIPT=str(script))
    p = subprocess.run([sys.executable, str(TESTS)], capture_output=True, text=True, env=env)
    out = p.stdout + p.stderr
    failed = sorted({line.split()[1] for line in out.splitlines() if line.startswith(("FAIL:", "ERROR:"))})
    return p.returncode, failed, out


def main():
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    target = HERE / spec["target"]
    source = target.read_text(encoding="utf-8")

    code, failed, out = run_suite(target)
    if code != 0:
        print(f"✗ the suite is not green on the real {spec['target']} — fix that first:\n{out[-2000:]}")
        return 1
    print(f"✓ real {spec['target']}: suite passes")

    ok = True
    for m in spec["mutants"]:
        n = source.count(m["find"])
        if n != 1:
            print(f"✗ {m['id']}: STALE — its find text appears {n} times in {spec['target']}; update the mutant")
            ok = False
            continue
        tmp = Path(tempfile.mkdtemp(prefix=".broken-", dir=HERE))
        try:
            mutant = tmp / spec["target"]
            mutant.write_text(source.replace(m["find"], m["replace"]), encoding="utf-8")
            code, failed, _ = run_suite(mutant)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        if code == 0:
            print(f"✗ {m['id']}: NOT CAUGHT — the suite passed with this bug in ({m['breaks']})")
            ok = False
        elif m.get("expect_failing_test") and m["expect_failing_test"] not in failed:
            print(f"✗ {m['id']}: caught, but not by {m['expect_failing_test']} (failed: {', '.join(failed) or 'none listed'})")
            ok = False
        else:
            print(f"✓ {m['id']}: caught by {', '.join(failed)}")
    if target.read_text(encoding="utf-8") != source:
        print(f"✗ {spec['target']} changed during the run — it must never be edited")
        return 1
    print(("✓ all %d mutants caught" if ok else "✗ some mutants were not caught (%d total)") % len(spec["mutants"]))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
