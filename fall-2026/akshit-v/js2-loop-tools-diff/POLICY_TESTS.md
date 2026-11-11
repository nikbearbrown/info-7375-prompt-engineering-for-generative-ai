# Permission policy: boundary tests and predicted outcomes

Policy: GATE.md section 6. Code: `agent2/policy.py` and the redirect guard in `agent2/fetch.py`. Tests: `tests/test_policy_boundaries.py`.

**The predictions below were written on 2026-11-10 and committed before any of these tests was run.** Claude Code derived them directly from GATE.md section 6; I reviewed them before the first run. Results are filled in only after running (see the table at the end).

| # | Case | Request | Predicted outcome | Why (GATE.md §6) |
|---|---|---|---|---|
| B01 | Host off the allow-list | GET `https://evil.example.com/jobs` | **refused** | host not allowed |
| B02 | Look-alike host (suffix trick) | GET `https://boards-api.greenhouse.io.evil.example/…` | **refused** | the hostname must match exactly |
| B03 | Plain http on an allowed host | GET `http://api.lever.co/…` | **refused** | https only |
| B04 | POST to an allowed host | POST `https://api.lever.co/…/apply` | **refused** | GET only; the agent never applies |
| B05 | GET to an allowed host | GET `https://api.ashbyhq.com/…/snowflake` | **allowed** | on the allow-list, https, GET |
| B06 | Redirect to an off-list host | 302 to `https://evil.example.com/` | **refused** | redirects must stay on the allow-list |
| B07 | Write inside `out/` | write `out/state/seen_ids.json` | **allowed** | writes go inside `out/` |
| B08 | `..` escape | write `out/../GATE.md` | **refused** | resolves outside `out/` |
| B09 | Prefix trick: sibling folder | write `out-evil/x.json` | **refused** | `out-evil` is not inside `out` |
| B10 | Link inside `out/` pointing outside | write `out/escape/x.json`, where `escape` links to a folder outside (a junction on Windows, a symlink on POSIX) | **refused** | resolves outside `out/` |
| B11 | Absolute path outside | write `<elsewhere>/x.json` | **refused** | outside `out/` |
| B12 | Read versus write, same file | read `GATE.md`, then write `GATE.md` | read **allowed**, write **refused** | reads are allowed in the project; writes only in `out/` |
| B13 | Read outside the project | read `<elsewhere>/anything.txt` | **refused** | reads only inside the project folder |
| B14 | Reset state without approval | `reset_state` with no approval | **refused (needs approval)**, file still there | resetting state needs `--approve reset-state` |
| B15 | Reset state with approval | `reset_state` with `reset-state` approved | **allowed**, file deleted | approval given |

## Results after running

First run: by me, in my own terminal, on 2026-11-10 (`python -B -m unittest discover -s tests -t . -v`). The output is saved in `review/test_run_1_before_patch.txt`.

| # | Predicted | Actual |
|---|---|---|
| B01–B06 | refused (except B05: allowed) | **as predicted**: all 6 passed |
| B07–B11 | allowed for B07; refused for B08–B11 | **as predicted**: all 5 passed (B10 ran as a real Windows junction) |
| B12 | read allowed, write refused | **as predicted** |
| B13 | refused | **as predicted** |
| B14 | refused (needs approval), file kept | **as predicted** |
| B15 | allowed, file deleted | **as predicted** |

All 15 outcomes matched the predictions. No prediction was changed after the run.
