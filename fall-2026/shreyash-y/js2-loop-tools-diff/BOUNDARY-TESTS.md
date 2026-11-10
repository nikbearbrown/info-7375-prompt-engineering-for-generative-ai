# Permission policy: boundary tests and predictions

*The predictions were written by Claude Code on 2026-11-09 from GATE.md section 6 and GATE-NOTES.md, and committed with the tests before `jsagent/policy.py` existed. The "Result" column is filled in only after running `python3 -m unittest tests.test_policy -v`. Each row is one test in `tests/test_policy.py`.*

| # | Case | Request or path | Predicted | Why | Result |
|---|---|---|---|---|---|
| 1 | Host off the allow-list | GET `https://evil.example.com/v1/boards/oscar/jobs` | refused: host | not one of the three hosts | |
| 2 | Look-alike host | GET `https://boards-api.greenhouse.io.evil.com/v1/boards/oscar/jobs` | refused: host | the real host is `…evil.com` | |
| 3 | Plain http | GET `http://api.lever.co/v0/postings/palantir` | refused: scheme | https only | |
| 4 | Userinfo trick | GET `https://api.lever.co@evil.example.com/v0/postings/x` | refused: host | the host is evil.example.com | |
| 5 | Allowed host, wrong path (an apply endpoint) | GET `https://boards-api.greenhouse.io/v1/boards/oscar/jobs/123/applications` | refused: path | only the job-list path is allowed | |
| 6 | Allowed URL, write method | POST `https://api.ashbyhq.com/posting-api/job-board/linear` | refused: method | GET only, so the agent cannot apply or submit anything | |
| 7 | Redirect off the list | 302 from an allowed URL to `https://evil.example.com/` | refused: host | redirects go through the same check | |
| 8 | Allowed request | GET `https://api.ashbyhq.com/posting-api/job-board/linear` | allowed | host and path on the list | |
| 9 | Path escape with `..` | write `runs/../GATE.md` | refused: outside runs/ | resolves to the folder root | |
| 10 | Prefix trick | write `runs-evil/x.json` | refused: outside runs/ | `runs-evil` is not inside `runs` | |
| 11 | Symlink out | write `runs/link/x.json`, where `runs/link` points to a temp folder outside | refused: outside runs/ | the real path is outside | |
| 12 | Absolute path | write `/tmp/x.json` | refused: outside runs/ | | |
| 13 | Write outside runs/ but inside the folder | write `budgets.json` | refused: outside runs/ | the agent cannot raise its own budgets | |
| 14 | New evidence file | write a new `runs/<run>/raw/x.json` | allowed | new file inside runs/ | |
| 15 | Overwrite saved state, no approval | write over an existing `runs/state/state-old.json` | refused: needs approval | GATE.md section 6 | |
| 16 | The same, with approval | the same write, `approve=True` | allowed | approval given | |
| 17 | Delete raw evidence, no approval | delete an existing `runs/old/raw/x.json` | refused: needs approval | GATE.md section 6 | |
| 18 | Append to own trace | append to `runs/<run>/trace.jsonl` created in this run | allowed | not saved evidence from an earlier run | |
| 19 | Read inside the folder | read `GATE.md` | allowed | reads are allowed in the folder | |
| 20 | Read outside the folder | read `~/.ssh/config` | refused: read outside folder | | |
