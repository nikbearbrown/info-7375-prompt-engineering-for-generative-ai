# Evidence redactions (recorded by Claude Code, 2026-11-10)

| File | What changed | Original sha256 (kept locally, unpublished) | Published sha256 |
|---|---|---|---|
| `review/prepatch_failure.txt` (Aditya's pre-patch capture, saved 17:04 EST) | The macOS username in pytest's temp path, `pytest-of-<username>`, was replaced by `pytest-of-<user>` on 3 lines (5, 51, 52). No other byte changed: the assertion, the message, the counts and the exit status are as captured. | `166b97741c74ee2422f9fc6721580afeb414e915af96ae4128cb69f42820479e` | `356dd3c6651c58546a24c1107e73359c7f5f3ededdb6f5210bb5cceb748f13bd` |

The other four files Aditya supplied (`review/investigation_output_P2.txt`, `review/INVESTIGATION.md`, `tests/test_aditya_total_mismatch.py`, `review/CHANGE_REQUEST.md`) are committed byte-identical to what he saved.
