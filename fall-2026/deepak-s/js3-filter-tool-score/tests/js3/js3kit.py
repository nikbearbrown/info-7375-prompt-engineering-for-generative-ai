"""Shared helpers for the JS3 tests. Puts tests/js2 on sys.path so the JS2 test kit (js2kit.py,
checks.py) is reused without changing it. Named js3kit, not conftest: the JS2 tests import from
the root tests/conftest.py by module name."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_JS2 = str(ROOT / "tests" / "js2")
if _JS2 not in sys.path:
    sys.path.insert(0, _JS2)
