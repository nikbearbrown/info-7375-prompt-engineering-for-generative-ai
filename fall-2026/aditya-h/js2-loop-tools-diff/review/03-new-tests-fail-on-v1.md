# Step 3 — Aditya's revision tests fail on patch v1 (2026-11-10)

Aditya appended the class `CheckRefusesWrongFileInsideFolder` to `tests/test_review_check_reads.py` (the test text was drafted by Claude Code; Aditya created and ran it) and ran it in their own terminal on patch v1 (`d058733`). Output pasted into chat, abridged and verbatim:

```text
FAIL: test_other_runs_raw_file_refused (...CheckRefusesWrongFileInsideFolder...)
    with self.assertRaises(PermissionError):
AssertionError: PermissionError not raised
Ran 5 tests in 0.010s
FAILED (failures=3)
```

The three failures are the three in-folder wrong-file cases:
- another run's raw file,
- another board's raw file,
- a non-raw file in the folder.

The two passing tests are the outside-folder refusal and "this run's raw for this board still works". That is the defect Aditya chose to close, now pinned by a failing test.
