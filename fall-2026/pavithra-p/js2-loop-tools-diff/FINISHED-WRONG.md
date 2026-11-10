# A finished wrong answer, and the check that catches it

**The wrong version:** wrong version 3 in `GATE.md` and `agent/wrong_versions.py`. It is the real loop with one hook changed: a board that failed is counted as checked with 0 jobs. It is never used by the watcher; it runs only with `--wrong-version 3`, writes its own state file (`runs/state/seen_ids-WRONG-V3.json`) and puts `WRONG-V3` in every file name.

**The run (2026-11-10T13:31:00Z, in my own terminal):**

```bash
python3 -m agent watch --wrong-version 3
```

It ended cleanly, with exit status `finished` ("all 5 boards checked"), and reported `lever:no-such-board` as checked with 0 jobs. That is wrong: the board does not exist, and Lever answered HTTP 404. The agent's own report gives no sign of it. Report: `runs/20261110T133100Z-WRONG-V3/report.md`.

**The independent check:**

```bash
python3 -m agent check runs/20261110T133100Z-WRONG-V3
```

`agent/check.py` does not trust the report's counts. For every board the report calls checked, it opens the response body that was actually saved and parses it again. Its output:

```text
CHECK FAILED
- the run ended `finished`, but its report does not match its own evidence
- lever:no-such-board: reported as checked with 0 jobs, but the saved response (evidence/raw/20261110T133100Z-WRONG-V3-lever-no-such-board-a1.json, HTTP 404) is not a job list: expected a list of postings
```

The saved body is Lever's `{"ok": false, "error": "Document not found"}`.

**The same check on the real run** (`runs/20261110T133054Z`, 4 seconds earlier, same boards) passed, because the real loop reported that board as failed, and the run ended `incomplete`, not `finished`.

**Also:** I ran the same command a second time by accident at 13:31:22Z. That run (`runs/20261110T133122Z-WRONG-V3`) ended the same way, and the check failed it the same way. Both are kept.

**Covered by a test:** `test_catches_wrong_version_3_failed_board_reported_as_empty` (tests/test_wrong_versions.py) runs the same pair on constructed boards: the real loop ends `incomplete` and passes the check; wrong version 3 ends `finished` and fails it.

**What this check would still miss:** a board that answers HTTP 200 with a real but empty job list. The saved response would be a valid job list with 0 jobs, so the check would agree with a report of 0 jobs, even if the board had jobs a minute earlier.
