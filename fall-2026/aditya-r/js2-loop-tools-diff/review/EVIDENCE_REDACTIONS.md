# Evidence redactions (recorded by Claude Code, 2026-11-10)

| File | What changed | Original sha256 (kept locally, unpublished) | Published sha256 |
|---|---|---|---|
| `review/prepatch_failure.txt` (Aditya's pre-patch capture, saved 17:04 EST) | The macOS username in pytest's temp path, `pytest-of-<username>`, was replaced by `pytest-of-<user>` on 3 lines (5, 51, 52). No other byte changed: the assertion, the message, the counts and the exit status are as captured. | `166b97741c74ee2422f9fc6721580afeb414e915af96ae4128cb69f42820479e` | `356dd3c6651c58546a24c1107e73359c7f5f3ededdb6f5210bb5cceb748f13bd` |
| `review/aditya_postpatch_run.txt` (Aditya's own post-patch review run, 17:30:08–17:30:10 EST) | The absolute local path to this folder in pytest's `-v` header was replaced by `<js2>` on 2 lines (6, 7). No other byte changed. | `4a1b1ed2d84de601b6dd593d353f8cac235b71fe530b83a0c3138338fe351c51` | `1e2d44650a84475b39131ecf3eadf1898f54f5ddc744271f7bfab4f6a5fcfadc` |

The other four files Aditya supplied for the reproduction (`review/investigation_output_P2.txt`, `review/INVESTIGATION.md`, `tests/test_aditya_total_mismatch.py`, `review/CHANGE_REQUEST.md`) are committed byte-identical to what he saved.

Aditya's terminal screenshots of the review commands are kept locally and not published, because they show his username and host. The saved log is the published evidence. Its execution times are the times recorded inside the log, not the screenshot file names.
