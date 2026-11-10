"""Prove the wrong-version tests can fail: replace the audit with one that accepts everything
and confirm the W1/W2 tests go red. Run: python3 scripts/sabotage_check.py"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import jsagent.audit as audit  # noqa: E402

audit.audit_verdicts = lambda *a: []
suite = unittest.defaultTestLoader.loadTestsFromName("tests.test_wrong_versions")
result = unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w")).run(suite)
print(f"With the audit disabled: {len(result.failures)} of {result.testsRun} wrong-version tests failed "
      f"(expected 9: every W1/W2 test; W3 and W4 test state logic, not the audit).")
sys.exit(0 if len(result.failures) == 9 else 1)
