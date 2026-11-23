# Boundary tests: the permission policy (GATE.md)

The 19 cases test the permission policy in GATE.md v1.0: which hosts, paths and methods a request may use, where the agent may write and read, and which writes need my `--approve`.

**My predictions** are the words I typed in chat on 2026-11-08 at 4:50 PM ET, before any boundary test was written or run: allow (it goes ahead), refuse (it is blocked), or approval (it is blocked unless I pass `--approve`). Claude Code wrote the 19 cases on 2026-11-07 and this table; the predictions are mine, copied word for word. The Actual column comes later, from running `tests/test_boundary.py`.

| # | Action | My prediction | Actual | Match |
|---:|---|---|---|---|
| 1 | GET `https://evil.example/posting-api/job-board/openai` | refuse | refuse | yes |
| 2 | GET `https://api.lever.co.evil.example/v0/postings/palantir?mode=json` | refuse | refuse | yes |
| 3 | GET `https://api.lever.co@evil.example/v0/postings/palantir?mode=json` | refuse | refuse | yes |
| 4 | GET `http://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true` (http) | refuse | refuse | yes |
| 5 | GET `https://api.lever.co/v0/postings/palantir/abc123/apply` | refuse | refuse | yes |
| 6 | POST `https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true` | refuse | refuse | yes |
| 7 | GET `https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true` | allow | allow | yes |
| 8 | api.lever.co answers with a redirect to another host | allow | refuse | **no** |
| 9 | Write `runs/../persona/jane-doe.json` | refuse | refuse | yes |
| 10 | Write `runs-evil/report.md` (a folder beside `runs/`) | refuse | refuse | yes |
| 11 | Write `runs/out-link/report.md`, where `out-link` is a symlink to a folder outside the repo | refuse | refuse | yes |
| 12 | Write `/tmp/report.md` | refuse | refuse | yes |
| 13 | Read `persona/jane-doe.json` | allow | allow | yes |
| 14 | Write `persona/jane-doe.json` | refuse | refuse | yes |
| 15 | Write the first state for a board that has none (`state/greenhouse-verkada.json`) | allow | allow | yes |
| 16 | Add newly seen ids to a board's existing state, removing none | allow | allow | yes |
| 17 | Replace a board's state with one that drops ids, without `--approve` | approval | approval | yes |
| 18 | Same as 17, with `--approve "reason"` | allow | allow | yes |
| 19 | Delete a board's state file, without `--approve` | approval | approval | yes |

18 of 19 predictions match. The Actual column and the section below come from `python3 tools/boundary_table.py`, which runs the same cases as `tests/test_boundary.py`; `--check` reruns them and compares.

## What the program said

1. **refuse**: refused: host 'evil.example' is not on the allow-list (api.ashbyhq.com, api.lever.co, boards-api.greenhouse.io)
2. **refuse**: refused: host 'api.lever.co.evil.example' is not on the allow-list (api.ashbyhq.com, api.lever.co, boards-api.greenhouse.io)
3. **refuse**: refused: 'https://api.lever.co@evil.example/v0/postings/palantir?mode=json' names a user or password
4. **refuse**: refused: 'http://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true' is not https
5. **refuse**: refused: 'https://api.lever.co/v0/postings/palantir/abc123/apply' is not a board path the agent may read on api.lever.co
6. **refuse**: refused: POST 'https://boards-api.greenhouse.io/v1/boards/verkada/jobs?content=true': the agent sends GET requests only
7. **allow**: sent once through the network door; the stand-in opener answered HTTP 200
8. **refuse**: the board answered 302 with a redirect to 'https://evil.example/v0/postings/palantir?mode=json'; redirects are not followed
9. **refuse**: refused: write runs/../persona/jane-doe.json: a path with '..' is never followed
10. **refuse**: refused: write runs-evil/report.md: outside the folders the agent may write (runs, state)
11. **refuse**: refused: write runs/out-link/report.md: out-link is a symlink, and symlinks are never followed
12. **refuse**: refused: write /tmp/report.md: outside the folders the agent may write (runs, state)
13. **allow**: allowed: persona/jane-doe.json
14. **refuse**: refused: write persona/jane-doe.json: outside the folders the agent may write (runs, state)
15. **allow**: first
16. **allow**: append
17. **approval**: refused: write state/greenhouse-verkada.json would replace a board's state (1 seen id would be dropped); this needs --approve
18. **allow**: approved
19. **approval**: refused: deleting state/greenhouse-verkada.json would remove a board's state; this needs --approve
