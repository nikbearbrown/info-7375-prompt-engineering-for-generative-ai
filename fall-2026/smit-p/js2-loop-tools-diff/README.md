# Job-Search Agent 2 — The Loop, the Tools, and the Diff

Smit P · INFO 7375 Fall 2026 · Chapters 4–6 ·
[Course AI policy](https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/blob/main/prerequisites/ai-policy.md)
· [AI Policy for Professor Bear's Courses | Using AI Responsibly in Class](https://youtu.be/8Ut0Cdl6vMw?si=9w3aEpt1ZyAR4Kiz)

A bounded loop that watches three public job boards on three different applicant-tracking
systems (Greenhouse, Lever, Ashby), plus one board that fails on purpose. Every
request and every file write goes through a permission policy enforced in code, every
observation is traced, and a separate checker that shares no code with the agent re-verifies
each run from the saved raw responses. Built in one Claude Code session on 2026-11-08; see
[SOURCES.md](SOURCES.md) for exactly what Claude Code did and what is left to Smit.

## Language, toolchain, commands

Python 3, standard library only. Developed and run on Python 3.13.17 on Linux; older
versions were not tried. No
`pip install`, no API keys, no model calls. The tests run offline.

From a fresh clone:

```bash
cd fall-2026/smit-p/js2-loop-tools-diff
```

Run the offline test suite (59 tests):

```bash
python3 -m unittest discover -s tests -t .
```

Check that the tests catch each wrong version listed in GATE.md (plants 10 mutants in a scratch copy):

```bash
python3 tests/mutation_check.py
```

One live run against the real boards (about 3 s, 4 requests). It prints a run id and exits 0 / 2 / 3 / 1 for finished / incomplete / budget_exhausted / error:

```bash
python3 run_agent.py
```

Independent check of that run (use the run id it printed):

```bash
python3 verify_run.py <run-id>
```

Replay a labeled seeded scenario (run ids must start with `seeded-` and be new):

```bash
python3 run_agent.py --boards fixtures/vanish/boards.json --replay fixtures/vanish/scenario-2-figma-empty.json --run-id seeded-try-1
```

A live run against the deliberate bad board ends `incomplete` with exit code 2. That is the
designed result, not a crash.

## What is here

| File | What |
|---|---|
| [GATE.md](GATE.md) | Exits, budgets, repeat rule, error policy, permission policy, wrong versions. Committed before any code (`f150426`). |
| [POLICY.md](POLICY.md) | 25 boundary cases predicted before the code (`2b3563e`), then the results: 25/25 matched. |
| [WRONG_ANSWER.md](WRONG_ANSWER.md) | A seeded run that ends `finished` and is wrong, and the independent check that catches it. |
| [REVIEW_PACKET.md](REVIEW_PACKET.md) | One change: defect reproduced, test committed first, diff read as behavior, scope, a revised first patch, decision (Smit's to make). |
| [SIGNOFF.md](SIGNOFF.md) | Sign-off draft and driver's seat table. **Unsigned until Smit signs.** |
| [SOURCES.md](SOURCES.md) | Starting point, endpoints, what Claude Code contributed. |
| [FRICTIONAL.md](FRICTIONAL.md) | Session record (Claude's, labeled) and Smit's entries. |
| `agent/policy.py` | Host allow-list, read/write roots, approval-gated writes, forbidden actions. |
| `agent/fetch.py` | The only network path: policy check, per-host 1 s gap, no redirects, explicit User-Agent; live and replay transports. |
| `agent/loop.py` | The loop: budgets, exits, repeat rule, error policy, trace, state. |
| `agent/adapters.py` | Greenhouse / Lever / Ashby JSON to postings. |
| `run_agent.py` | Command line. |
| `verify_run.py` | Independent checker. Imports nothing from `agent/`. |
| `tests/` | `test_policy.py` (boundaries), `test_loop.py`, `test_empty_after_nonempty.py` (review packet), `test_redirect.py`, `mutation_check.py`. |
| `config/` | `boards.json`, `budgets.json`. Writes here need approval. |
| `fixtures/` | Seeded scenarios. Bodies point at real saved responses, except `figma-empty-SEEDED.json`, which is hand-written. |
| `jobs/runs/<run-id>/` | `trace.jsonl`, `summary.json`, `raw/` (the saved raw responses) for every run. |
| `jobs/state/` | Live baseline per board. Seeded runs use `jobs/seeded-state/` and never touch this. |
| `evidence/` | Saved command output cited by the documents. |

## What ran

All on 2026-11-08 (UTC). "Live" means real HTTPS calls to the public endpoints; "seeded"
means saved responses replayed and labeled as such.

| Run | Kind | Code | Result | Independent check |
|---|---|---|---|---|
| `2026-11-08T00-43-54Z` | live | v1 | figma 145, bad name 404 → null, spotify 85, linear 32; baseline; `incomplete` | passed |
| `2026-11-08T00-47-30Z` | live | patched | same counts, 0 new; `incomplete` | passed |
| `2026-11-08T00-48-58Z` | live | patched + no-redirect | same counts, 0 new; `incomplete` | passed |
| `seeded-vanish-1..3` | seeded | v1 | **`finished` while Figma was empty**; then 145 old postings reported as new | **failed** run 2 |
| `seeded-vanishfix-1..4` | seeded | patched | run 2 (first patch) failed the check on count 0; run 3 (revised) `incomplete`, NEEDS HUMAN; run 4: 0 new | run 2 failed, run 3 passed |
| `seeded-timeouts-1` | seeded | patched | figma timed out then succeeded on retry; spotify timed out twice → `failed:unreachable`, null | — |

No posting changed during the minutes between the live runs, so "new posting" detection is
shown on seeded and unit-test data only. That is listed under "Not checked" in SIGNOFF.md.

### The trace of one real run, with the deliberate failure

`jobs/runs/2026-11-08T00-48-58Z/trace.jsonl`, fields trimmed for reading:

```text
 1 00:48:58.958 run_start
 2 00:48:58.958 request      figma  GET https://boards-api.greenhouse.io/v1/boards/figma/jobs
 3 00:48:59.345 response     figma  200  91874 bytes  386 ms
 4 00:48:59.348 board_result figma  ok  count=145
 5 00:48:59.349 request      deliberate-bad-name  GET .../boards/figma-no-such-board-js2/jobs
 6 00:49:00.485 response     deliberate-bad-name  404  38 bytes  host_gap_wait_s=0.995
 7 00:49:00.485 board_result deliberate-bad-name  failed:not_found  count=null   (no retry)
 8 00:49:00.486 request      spotify  GET https://api.lever.co/v0/postings/spotify?mode=json
 9 00:49:01.696 response     spotify  200  814089 bytes  1208 ms
10 00:49:01.702 board_result spotify  ok  count=85
11 00:49:01.703 request      linear  GET https://api.ashbyhq.com/posting-api/job-board/linear
12 00:49:01.861 response     linear  200  452742 bytes  156 ms
13 00:49:01.864 board_result linear  ok  count=32
14-16           state_write  figma 145→145, spotify 85→85, linear 32→32, new=0 each
17 00:49:01.868 run_end      exit=incomplete
```

The bad board got one request. A 404 is not retried, because asking again returns the same
answer (GATE.md error policy). It reports `count: null`, not 0, and the run says `incomplete`
with a `NEEDS HUMAN` line instead of claiming success. The 0.995 s wait on line 6 is the
per-host gap: it was the second request to Greenhouse within a second.

## Privacy

No résumé, persona, contact, or credential is used or stored. This layer only watches
boards. The agent cannot apply, email, message, or log in (GATE.md, enforced by
`check_request` and `check_action`).
