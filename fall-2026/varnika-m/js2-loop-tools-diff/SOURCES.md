# SOURCES — Job-Search Agent 2

What I used, what Claude contributed, and what I wrote, ran or decided myself. All dates are 2026-11-10.

## What I used

| Source | What I took from it |
|---|---|
| My JS1 folder, `../js1-contract-and-watch/` (commit `a70993c`) | `agent/rule.py`, copied byte-identical (SHA-256 `2aa42900…`). The fictional-résumé check, adapted into `agent/resume.py` (same two checks, on text instead of a file). The persona `persona/aarav-patel.resume.example.json`, unchanged (SHA-256 `f6ee24e4…`). The Anthropic state, 675 ids (SHA-256 `9d5d308a…`), and JS1's two raw responses as the board's history (`scripts/import_js1_state.py`) |
| The Reallocation Engine, `nikbearbrown/the-reallocation-engine` (my local copy, read only, commit `bb22533`), `scripts/ats/providers/lever.mjs` and `ashby.mjs` | The Lever and Ashby endpoints and field names (`text`, `hostedUrl`, `categories.location`; `jobs[]`, `jobUrl`, `location`). Rewritten in Python in `agent/boards.py`; no code was copied |
| Public job-board APIs: `boards-api.greenhouse.io/v1/boards/anthropic/jobs`, `api.lever.co/v0/postings/palantir`, `api.ashbyhq.com/posting-api/job-board/linear` | The postings the agent watches |
| The JS2 assignment brief | The steps, the sign-off format and the grading |

I did not use Lectern.

## Requests made outside the agent

Claude Code made these one-off requests while choosing boards and checking how a bad name fails. None of them was a run of the agent, and their copies were kept in Claude Code's scratch folder, not here.

| Time (UTC) | Requests | Result |
|---|---|---|
| about 19:35 | Greenhouse `anthropic` (without `content=true`); Lever `palantir?limit=1`; Ashby `openai` | 200, 200, 200 (Ashby `openai` was 13.9 MB, so it was not used) |
| 19:39:26 | a made-up board name on each of Greenhouse, Lever and Ashby | 404, 404, 404 |
| 19:39:33 | Lever `palantir`; Lever `plaid`; Ashby `linear`; Ashby `notion` | 200 (304 postings), 404, 200 (33), 200 (155) |

The agent itself made 12 requests: live runs 1, 2 and 3, four each. The tests, the finished-wrong demonstration and the independent reviewer contacted only `127.0.0.1` (the reviewer said so in its report).

## What Claude contributed

Claude Code (Opus 5.5, model `claude-opus-5-5`) in one Claude Code session in VS Code.

| Part | What Claude Code did | What I did |
|---|---|---|
| Explaining the assignment | Explained it in simple English; told me which repo to work in; explained that the assignment says I write GATE.md, and that Claude's help is allowed if it is recorded here | Asked |
| `GATE.md` | Drafted all of it: the boards, exits, budgets, repeat rule, error and permission policy, wrong versions W1–W12 and the independent check. It chose every number | Replied "ok" to keep the draft unchanged. It was committed before any code (`040be50`) |
| `POLICY.md` predictions | Wrote the predicted outcome of all 30 boundary cases, committed with the tests before any code existed (`76e0f89`) | — |
| `tests/` (122 tests) | Wrote all of them. Policy, loop, boards, gate-matches-code, check and wrong-version tests came before the code (`76e0f89`). The review packet test came before the patch (`8ddfec0`). The review-finding tests came before each fix (`7e09390`, `9a2179e`, `3e48c6c`). So did the time-budget tests (`304b599`) and the privacy tests (`4afa0b8`). After the code existed it fixed one test helper bug and **strengthened** B14 (`322da65`, described in the commit) | Ran the review test before the patch, and the whole suite after it |
| `agent/`, `check_run.py`, `scripts/` | Wrote all of them | — |
| Live runs | Ran live runs 1 and 3, and the seeded demonstration | Ran live run 2 myself |
| The review packet | Found the slow-trickle defect, wrote the test, patched (`91bfbda`), checked a 404 and the slow-headers case, drafted `REVIEW-PACKET.md`. When I asked what it thought, recommended REVISE with a guard test. Then wrote the guard test I asked for (`764c262`) | Ran the failing test before the patch; read the diff; ran the suite and live run 2; decided **REVISE**, in my own words (REVIEW-PACKET.md section 6) |
| The independent reviewer | Started a separate Claude reviewer **on its own initiative**. It reported 8 findings; Claude Code turned each into a test before fixing it, and wrote `REVIEW-FINDINGS.md` | Nothing yet on the two open findings (8b, 8c) |
| Finding 7b | Its own fix for finding 7 caused the wrong `gone` in my live run 2. It found that, wrote the tests, fixed it, and added `gone_recomputed` to `check_run.py` | My run 2 is the run that showed it |
| `README.md`, `FINISHED-WRONG.md`, this file | Drafted them from the record | |
| The sign-off and driver's seat | Drafted both in README.md; its sign-off draft is kept there, labeled as not signed | Wrote and signed my own sign-off (pasted in word for word); checked the driver's seat |
| `FRICTIONAL.md` | Drafted the factual lines of each entry; pasted my six "What I learned" lines in unchanged | Wrote the six "What I learned" lines |

**Claude responses shown in this folder.** The independent reviewer's report, which I received on 2026-11-10, is summarized in `REVIEW-FINDINGS.md`. Its scratch scripts are not included. Everything in `jobs/`, `finished-wrong/` and `review/` is program output, not Claude's words. The agent itself makes no call to Claude.

**Transcripts.** The Claude Code conversation transcript stays on my machine, following the assignment's privacy rule.

**Redaction (2026-11-10, at my request).** Eight saved files contained the absolute path of this folder, which includes my macOS username: the six run traces (in `jobs/runs/` and `finished-wrong/jobs/runs/`, where the policy named the state file it allowed) and the tracebacks in `review/1-…` and `review/2-…`. Claude Code replaced that path with `<js2-folder>` in those files and nothing else.
- The raw responses were not touched.
- `check_run.py` gives the same verdict on every run after the redaction.
- The code was changed first, so future runs name files relative to this folder (tests `4afa0b8` before the change `c10af62`).
- **The earlier commits still contain the unredacted files, because the git history was not rewritten.** Rewriting it would change every commit id cited in this folder.

## What I wrote, ran or decided

| Part | What |
|---|---|
| GATE.md | Kept Claude Code's draft unchanged by replying "ok" (committed `040be50`) |
| Review packet, before the patch | Ran `python3 -m unittest tests.test_transport_deadline -v` in my own terminal: 1 FAIL, 2 ok, 6.027 s ([review/2-before-patch-varnika-run.txt](review/2-before-patch-varnika-run.txt)) |
| Review packet, after the patch | Ran `python3 -m unittest discover -s tests -t .` (96 OK), read `git diff 8ddfec0 91bfbda -- agent/tools.py`, and ran live run 2, `python3 -m agent.loop`, at 21:45:09 UTC ([review/6-after-patch-varnika-run.txt](review/6-after-patch-varnika-run.txt)) |
| Review decision | REVISE: "The test should explicitly verify that the socket is found through ._sock and fail immediately if that attribute is missing, rather than allowing the code to silently continue." |
| Time-budget policy | My two decisions in GATE.md, Decisions, November 10, 2026: an invalid or unreliable time budget must stop the run; the independent check must enforce the same time budget. Claude Code wrote the tests first (`304b599`) and the changes (`71491b1`) |
| Removing my username | Asked for the folder path to be removed from saved files (see Redaction above) |
| FRICTIONAL "What I learned" lines | Wrote all six. Claude Code pasted them in word for word |
| Sign-off | Wrote it myself and signed it: "Signed, Varnika M, 2026-11-10" |
