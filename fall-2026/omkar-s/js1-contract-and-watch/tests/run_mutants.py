"""Run the whole test suite against each wrong version. Each must be KILLED (suite fails).
    python3 tests/run_mutants.py
Each mutant runs in its own interpreter so its monkeypatch can't leak."""
import glob
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CODE = ("import importlib,sys,unittest; importlib.import_module('tests.mutants.%s').apply(); "
        "r=unittest.TextTestRunner(verbosity=0).run(unittest.defaultTestLoader.discover('tests')); "
        "print('FAILED:', [t.id() for t,_ in r.failures+r.errors]); sys.exit(0 if r.wasSuccessful() else 1)")

survivors = 0
for path in sorted(glob.glob(os.path.join(ROOT, "tests", "mutants", "m*.py"))):
    name = os.path.splitext(os.path.basename(path))[0]
    p = subprocess.run([sys.executable, "-c", CODE % name], cwd=ROOT, capture_output=True, text=True)
    failed = [l for l in p.stdout.splitlines() if l.startswith("FAILED:")]
    status = "KILLED" if p.returncode != 0 else "SURVIVED"
    survivors += status == "SURVIVED"
    print(f"{status:9} {name}  {failed[0] if failed else ''}")
sys.exit(1 if survivors else 0)
