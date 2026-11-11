# Evidence redactions (recorded by Claude Code, 2026-11-10)

| File | What changed | Original sha256 (kept locally, unpublished) | Published sha256 |
|---|---|---|---|
| `review/prepatch_failure.txt` (Aditya's pre-patch capture, saved 17:04 EST) | The macOS username in pytest's temp path, `pytest-of-<username>`, was replaced by `pytest-of-<user>` on 3 lines (5, 51, 52). No other byte changed: the assertion, the message, the counts and the exit status are as captured. | `166b97741c74ee2422f9fc6721580afeb414e915af96ae4128cb69f42820479e` | `356dd3c6651c58546a24c1107e73359c7f5f3ededdb6f5210bb5cceb748f13bd` |
| `review/aditya_postpatch_run.txt` (Aditya's own post-patch review run, 17:30:08–17:30:10 EST) | The absolute local path to this folder in pytest's `-v` header was replaced by `<js2>` on 2 lines (6, 7). No other byte changed. | `4a1b1ed2d84de601b6dd593d353f8cac235b71fe530b83a0c3138338fe351c51` | `1e2d44650a84475b39131ecf3eadf1898f54f5ddc744271f7bfab4f6a5fcfadc` |
| `evidence/aditya_clean_clone_check.txt` (Aditya's own fresh-extraction check, 18:41:36–18:42:07 EST) | The macOS per-user temp folder in pip's upgrade notice, `/private/var/folders/…/T/tmp.<random>/`, was replaced by `<tmp>/` on 1 line (5). No other byte changed: the tested commit, the counts, the CAUGHT lines, the checker output and the exit status are as captured. | `2d03caa4fe6a80d9bea8327f9a72575db315a28bd7ab9019f06f8b6f8cc70a95` | `2445af4464b1d5d23ec6207928f9ab18c5750353cbe3aec7b2dedf9681c6aea6` |
| `evidence/aditya_final_verification.txt` (Aditya's final verification, 20:19:19–20:20:31 EST) | Two kinds of local temp-folder paths were replaced: the pre-fix extraction folder `/private/tmp/js2-deadline-before.<random>/` became `<before-tmp>/` on 4 lines (8–11), and pip's per-user temp folder became `<tmp>/` on 1 line (24). No other byte changed: the hashes, counts, CAUGHT lines, checker output and exit statuses are as captured. | `a0d51ce49ad528467a55d08415a02a475718430dbf7b40bca38e0a32cce0670e` | `bf6909516d75756c8def1bf4db783964bb7a7c6b0b32b14b86b7ca5ceecf3533` |

**Approval demonstration (Aditya, 18:36:37–18:38:11 EST).** These files are committed byte-identical to what his commands produced; none contained a private path:

| File | sha256 |
|---|---|
| `evidence/approval_demo.txt` | `c57ae7b1e0e74b2b9ddf94d450ba89bb11a333dbf0c512110231cb3e12eb3e43` |
| `approvals/20261110T232115022Z_live.json` (his approval record) | `a5f8bb0a109b04b73b84b9693f431d9908e269b54371304af50f6b470cfcecfc` |
| `out/approved-shortlists/20261110T232115022Z_live.json` (the export; equals the proposed bytes) | `df370075878e17c24f98c20e31b4108cb7daa51f60e5862b66a1b101999bbcc6` |
| `out/exports/*.result.json` (3 result records: exit 3, 0, 2) | written by `--export`; unchanged |

The other four files Aditya supplied for the reproduction (`review/investigation_output_P2.txt`, `review/INVESTIGATION.md`, `tests/test_aditya_total_mismatch.py`, `review/CHANGE_REQUEST.md`) are committed byte-identical to what he saved.

Aditya's terminal screenshots of the review commands are kept locally and not published, because they show his username and host. The saved log is the published evidence. Its execution times are the times recorded inside the log, not the screenshot file names.
