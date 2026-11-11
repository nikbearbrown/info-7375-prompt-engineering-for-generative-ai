# FRICTIONAL — Job-Search Agent 2

## Part A — my entries (Saloni, in my own words)

_(Saloni writes these. Dated, specific: what I tried, what happened, what I checked, what I
accepted / changed / rejected from Claude, and what is still unresolved. Link a commit or a
`review/` file in each.)_

### 2026-11-10 — 

### 2026-11-10 — 

### 2026-11-10 — 

### Still unresolved

## Part B — timeline of what happened (drafted by Claude Code from git and the run files)

All times 2026-11-10 ET (UTC in run ids is +5 h). Exact times are git commit times or `review/` file times; "~" times are from the chat session.

| Time (ET) | What | Evidence |
|---|---|---|
| ~19:18 | Claude couldn't find my JS1 folder; it was in the course repo. I pointed it at the JS1 zip and said to search; it found `fall-2026/saloni-m/js1-contract-and-watch/` | session |
| ~19:20–19:30 | Claude asked for my GATE decisions; I said I wasn't sure and asked for examples; I chose `1A fail=a, 2A, 3A, 4A, 5B` and rewrote three of the example wrong versions and the failure-sentence template in my own words | GATE.md |
| ~19:30 | Looked at what classmates had posted (structure and counts only); decided to keep 2 job systems rather than add Lever | session; SOURCES.md |
| ~19:33 | I asked whether we work on main; checked: every student commits to main in their own folder | session |
| 19:37 | **GATE.md committed alone, before any code** | `5d221da6` |
| 19:41 | Loop + policy + 24 offline tests | `83abeea8` |
| 19:41 (commit 19:42) | Live run 1: 3 boards ok (679 / 144 / 826), misspelled board 404, `incomplete` | `61312028` |
| 19:42 | Failing test for wrong version 3, before the patch; real data had 0 shared ids | `75a70e03` |
| 19:44 | Finished-wrong demo (SIMULATED) caught by the independent check | `out/demo/finished-wrong/` |
| 19:47 | **My 21 boundary predictions committed before the run** | `39dea2de` |
| 19:47 | Boundary run 21/21; my predictions 19/21 — I said Lever was approved (B03); I said deny for B21 | `e4ec7a53` |
| 19:50 | I read patch v1, reproduced the defect myself, ran 48 tests, ran live run 2 | `review/04`–`07` |
| 19:50–19:54 | Live run 2 (00:50 UTC) reported 0 new, but OpenAI had added *Account Director, Mid-Market \| Korea*. **I decided REVISE** | `review/08-saloni-decision-v1.md`, `08951265` |
| 19:54 | Migration test from real run-1/run-2 data, failing on v1 | `6a453ccf` |
| 19:55–19:56 | I read v2, ran 50 tests, live run 3 (1 new: Korea; approved history), live run 4 (0 new) | `review/11`–`14` |
| ~20:00 | The real-data migration test started failing: it read the live history file, which my approval in run 3 had changed. Claude pinned run 1's history as a fixture and showed the test still fails on v1 | `review/15`; `tests/fixtures/` |

## Part C — what I accepted, modified, or rejected from Claude (table drafted by Claude Code from the chat; Saloni checked it)

| Claude's suggestion | What I did | Where |
|---|---|---|
| example options for every GATE heading | accepted 1A/2A/3A/4A/5B. For §6 I picked three of Claude's example ideas — (a) empty board, (b) silent skip, (g) id collision — and rewrote each in my own words; §7 is my own sentence built on Claude's fill-in-the-blank template | GATE.md |
| add Lever as a third system? | I asked Claude what it recommended; it recommended keeping two (time; two meet the brief) and I agreed | session |
| patch v1 (re-baseline old history) | **revised**: it hid a real new job | `review/08` |
| patch v2 (migrate from saved raw) | _(my decision)_ | REVIEW-PACKET.md §3 |
| B21: needs approval rather than deny | left open, not changed | BOUNDARY-TESTS.md |
