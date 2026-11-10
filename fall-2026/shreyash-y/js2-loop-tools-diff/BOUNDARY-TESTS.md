# Permission policy: boundary tests and predictions

*The predictions were written by Claude Code on 2026-11-09 from GATE.md section 6 and GATE-NOTES.md, and committed with the tests before `jsagent/policy.py` existed. The "Result" column was filled in from the run on 2026-11-09 saved in `evidence/boundary-tests-run-2026-11-09.txt`: "as predicted" means the test asserting the prediction passed. Each row is one test in `tests/test_policy.py`.*

| # | Case | Request or path | Predicted | Why | Result |
|---|---|---|---|---|---|
| 1 | Host off the allow-list | GET `https://evil.example.com/v1/boards/oscar/jobs` | refused: host | not one of the three hosts | as predicted |
| 2 | Look-alike host | GET `https://boards-api.greenhouse.io.evil.com/v1/boards/oscar/jobs` | refused: host | the real host is `…evil.com` | as predicted |
| 3 | Plain http | GET `http://api.lever.co/v0/postings/palantir` | refused: scheme | https only | as predicted |
| 4 | Userinfo trick | GET `https://api.lever.co@evil.example.com/v0/postings/x` | refused: host | the host is evil.example.com | as predicted |
| 5 | Allowed host, wrong path (an apply endpoint) | GET `https://boards-api.greenhouse.io/v1/boards/oscar/jobs/123/applications` | refused: path | only the job-list path is allowed | as predicted |
| 6 | Allowed URL, write method | POST `https://api.ashbyhq.com/posting-api/job-board/linear` | refused: method | GET only, so the agent cannot apply or submit anything | as predicted |
| 7 | Redirect off the list | 302 from an allowed URL to `https://evil.example.com/` | refused: host | redirects go through the same check | as predicted |
| 8 | Allowed request | GET `https://api.ashbyhq.com/posting-api/job-board/linear` | allowed | host and path on the list | as predicted |
| 9 | Path escape with `..` | write `runs/../GATE.md` | refused: outside runs/ | resolves to the folder root | as predicted |
| 10 | Prefix trick | write `runs-evil/x.json` | refused: outside runs/ | `runs-evil` is not inside `runs` | as predicted |
| 11 | Symlink out | write `runs/link/x.json`, where `runs/link` points to a temp folder outside | refused: outside runs/ | the real path is outside | as predicted |
| 12 | Absolute path | write `/tmp/x.json` | refused: outside runs/ | | as predicted |
| 13 | Write outside runs/ but inside the folder | write `budgets.json` | refused: outside runs/ | the agent cannot raise its own budgets | as predicted |
| 14 | New evidence file | write a new `runs/<run>/raw/x.json` | allowed | new file inside runs/ | as predicted |
| 15 | Overwrite saved state, no approval | write over an existing `runs/state/state-old.json` | refused: needs approval | GATE.md section 6 | as predicted |
| 16 | The same, with approval | the same write, `approve=True` | allowed | approval given | as predicted |
| 17 | Delete raw evidence, no approval | delete an existing `runs/old/raw/x.json` | refused: needs approval | GATE.md section 6 | as predicted |
| 18 | Append to own trace | append to `runs/<run>/trace.jsonl` created in this run | allowed | not saved evidence from an earlier run | as predicted |
| 19 | Read inside the folder | read `GATE.md` | allowed | reads are allowed in the folder | as predicted |
| 20 | Read outside the folder | read `~/.ssh/config` | refused: read outside folder | | as predicted |
| 21 | Symlink that stays inside runs/ (added 2026-11-10 after review) | write `runs/alias.json`, a symlink to a not-yet-existing `runs/r1/target.json` | refused: symlink, and no file appears at the target | the real path is inside runs/ and the target does not exist yet, so only the explicit no-symlink rule can stop the write through the link | as predicted (`evidence/boundary-row21-run-2026-11-10.txt`) |
| 22 | Nested symlinks (added 2026-11-10 after a second review) | write `runs/hop1/x.json`, where `runs/hop1` links to `runs/hop2` and `runs/hop2` links to a folder outside | refused: outside runs/, and nothing appears outside | each link on its own looks like it stays in runs/; only following the whole chain shows the real path is outside | as predicted (`evidence/boundary-row22-run-2026-11-10.txt`) |

### BOUNDARY-21: an internal dangling symlink (added 2026-11-10, after review)

- **Setup.** A symlink `runs/alias.json` pointing to `runs/r1/target.json`, which does not exist. Both are inside `runs/`.
- **Operation.** Write through the symlink with the agent's permission-controlled write, `policy.Files.write`.
- **Prediction, recorded before execution: DENY.** Committed with the test in `2b8ed44`, before it was ever run.
- **Reason.** The permission policy refuses to write through a symlink even when its real destination is inside the authorized folder.
- **Expected evidence.** The permission layer raises before anything is created. The target file does not exist afterwards, and the symlink is unchanged: still a link, pointing to the same path.
- **Failure condition.** The write succeeds, or the policy allows it only because the destination stays inside `runs/`.
- **What happened.**
  - **No implementation change was made.** The no-symlink line has been in `jsagent/policy.py` since `f4b553d`. This row adds coverage for it; it is not a fix, so there is no "failing before the fix" run to show.
  - **On the unchanged code:** DENY, as predicted (`evidence/boundary-row21-run-2026-11-10.txt`, recorded in `119bdb7`).
  - **Evidence that the test can fail:** with the no-symlink line deleted in a scratch copy, row 21 fails and is the only test that does (`evidence/mutation-check-2026-11-09.txt`, second part). Before row 21 existed, the same deletion left every test green.
  - **The link-unchanged assertions** were added at review, after the first run. The file's sha256 in `tests.frozen.sha256` was updated, and the new run is in the same evidence file.

### What these 22 rows do not cover

- **The gap between checking a path and writing it** (a time-of-check/time-of-use race). `Files.write` resolves and checks the path, then opens it. If another process swapped a folder for a symlink in between, the write could follow it. No test covers this. Closing it properly means opening with `O_NOFOLLOW` relative to an already-opened `runs/` directory, which was not built. The agent is the only writer in `runs/` during a run, but that is an assumption, not something enforced.
- **Hard links.** A hard link inside `runs/` to a file outside is not detected.

**What row 11 does and does not prove** (written 2026-11-09, before row 21 existed). It passes because the resolved real path is outside `runs/`. The separate "never write through a symlink" line in `Files._writable` is not what makes it pass: deleting that line in a scratch copy left every test green (`evidence/mutation-check-2026-11-09.txt`). That line is a second layer that no test exercises on its own. **Closed on 2026-11-10 by row 21** (`tests/test_policy_symlink.py`), which only that line can pass: with it deleted, row 21 now fails (`evidence/mutation-check-2026-11-09.txt`, second part).
