"""Run every test_* function in the tests/test_*.py modules without pytest: python tests/run_tests.py [module ...]"""
import importlib
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
for s in (sys.stdout, sys.stderr):
    s.reconfigure(encoding="utf-8")
mods = sys.argv[1:] or sorted(p.stem for p in HERE.glob("test_*.py"))
failed = total = 0
for m in mods:
    mod = importlib.import_module(m)
    for name in sorted(n for n in dir(mod) if n.startswith("test_")):
        total += 1
        try:
            getattr(mod, name)()
            print(f"PASS {m}.{name}")
        except Exception:
            failed += 1
            print(f"FAIL {m}.{name}\n{traceback.format_exc()}")
print(f"{total - failed}/{total} passed")
sys.exit(1 if failed else 0)
