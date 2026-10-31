"""Run every test_wv_NN in tests/test_wrong_versions.py without pytest: python tests/run_tests.py"""
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_wrong_versions as t  # noqa: E402

for stream in (sys.stdout, sys.stderr):
    stream.reconfigure(encoding="utf-8")
tests = sorted(n for n in dir(t) if n.startswith("test_wv_"))
failed = 0
for name in tests:
    try:
        getattr(t, name)()
        print(f"PASS {name}")
    except Exception:
        failed += 1
        print(f"FAIL {name}\n{traceback.format_exc()}")
print(f"{len(tests) - failed}/{len(tests)} passed")
sys.exit(1 if failed else 0)
