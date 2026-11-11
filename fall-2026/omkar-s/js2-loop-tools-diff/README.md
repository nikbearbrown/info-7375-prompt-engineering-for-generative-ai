# Job-Search Agent 2: The Loop, the Tools, and the Diff

**Omkar Salian (omkar-s) · INFO 7375 Fall 2026 · Chapters 4–6**

My JS1 agent watched one Greenhouse board. This version is a **bounded loop** over **6 boards on 3 applicant-tracking systems** (Greenhouse, Ashby, Lever). Every request and every file write passes through a **permission policy enforced in code** (`agent/policy.py`). Every run ends in exactly one of four exits: `finished`, `incomplete`, `budget_exhausted`, `error`. Every request is recorded as an observation in `trace.jsonl`, next to the raw bytes it returned. The persona is still the **fictional** Aarav Patel. The rule is still my JS1 contract v2, copied unchanged.

**Started from:** my JS1 (`../js1-contract-and-watch/`): `rule.py`, `persona.py` and the persona are byte-identical copies. ATS endpoints and slug traps were taken from the instructor's **Lectern** (`fall-2026/nik-bear-brown/lectern/ATS.md`), read as a reference; no code was copied.

> **Status (2026-11-10):** the agent, tests and docs were built and run by **Claude Code** on 2026-11-09 while Omkar was offline. The parts that must be Omkar's own are marked **[Omkar]**, and **Omkar wrote them himself on 2026-11-10**: the GATE.md confirmations, the drop rule (GATE change log) and its review decision (REVIEW-PACKET "Second review"), the first review's decision, his own test runs, the sign-off with his own "Not checked" list, the driver's-seat "why", and FRICTIONAL Part 1.

## Toolchain

| | |
|---|---|
| Language | **Python 3**, standard library only. No `pip install`. Tested on **3.14.2** (python.org build), written for ≥ 3.10 |
| OS | macOS 15 (Darwin 24.6) |
| Network | HTTPS GET to `boards-api.greenhouse.io`, `api.ashbyhq.com` and `api.lever.co` only. No login, no keys, no Claude API calls |
| TLS | verification always on. If Python ships without a CA bundle (python.org macOS), it falls back to `/etc/ssl/cert.pem` (same fix as JS1) |

## Commands (from a fresh clone)

```bash
cd fall-2026/omkar-s/js2-loop-tools-diff

# all tests (offline: no network, about 0.3 s)
python3 -m unittest discover -s tests -t . -v

# the 14 wrong versions (GATE.md section 6, plus W10b and W11-W13 from the change log) must each be KILLED (a control run must pass first)
python3 tests/run_mutants.py

# one live run of the main watch list (6 boards; the 6th fails on purpose)
python3 -m agent.loop                     # = --watchlist config/watchlist.json --budgets config/budgets.json --out runs
echo $?                                   # 0 finished · 3 incomplete · 4 budget_exhausted · 5 error

# the independent check of a run (live cross-probe of any empty board)
python3 -m verify.independent_check runs/<run-folder>

# the finished-wrong-answer list, and the two exit demos (labelled DEMO configs)
python3 -m agent.loop --watchlist config/wrong-answer-watchlist.json --out runs/wrong-answer-demo
python3 -m agent.loop --budgets config/budgets-demo-tight.json --out runs/budget-demo
python3 -m agent.loop --watchlist config/error-demo-watchlist.json --out runs/error-demo
```

A live run from a fresh clone diffs against the state saved in `runs/state/` on 2026-11-09, so it reports what changed since then. Each run writes a new folder `runs/<UTC time>[-label]/`. The policy refuses to overwrite an earlier run.

## What is in this folder

| Path | What |
|---|---|
| `GATE.md` | Exits, budgets, repeat rule, error policy, permission policy, wrong versions. Written **before** any code (08:01 UTC). Frozen copy in `evidence/` |
| `POLICY.md` | The permission policy and the **boundary table: 21 cases predicted before `policy.py` existed, plus 1 added later (B16b)**, then the actual results |
| `TRACE.md` | Walkthrough of one real run's trace, including the deliberate failure, plus the real runs behind each of the four exits |
| `WRONG-ANSWER.md` | The run that finished cleanly (exit 0) and was wrong, and the independent check that caught it |
| `REVIEW-PACKET.md` | The reviewed change: defect reproduced → test before patch → diff read as behavior → scope → decision → what it still misses |
| `agent/` | `policy.py` (decisions), `transport.py` (the only network code), `store.py` (the only write code), `ats.py` (3 ATS adapters), `loop.py` (the loop), and `rule.py` + `persona.py` (from JS1, unchanged) |
| `verify/independent_check.py` | Re-derives a run's facts from raw bytes and outside evidence. Does not import the loop |
| `tests/` | 75 tests (66 + 9 for the drop rule); `mutants/` + `run_mutants.py` (14 wrong versions, with a control run); `fixtures/` (**constructed**, see its README) |
| `config/` | `watchlist.json`, `budgets.json`, `reference-counts.json`, and labelled DEMO configs |
| `runs/` | Every real run (traces before 08:29 contain absolute local paths; later ones are relative): `trace.jsonl`, `raw/` (**saved raw responses**), `report.json/.md`, `console.txt`; `state/` |
| `review/` | `before/loop.py` (pre-patch), `before/loop-v1.py`, `before/loop-v2-reviewed.py`, the diffs, the test output before and after each patch, and the later unrelated fix `later-fixes-after-review.diff` |
| `evidence/` | `TIMELINE.md` (order of work, with hashes), pre-build `probes/`, frozen GATE/POLICY copies, `test-runs/`, `agent-mtimes.txt` |
| `SOURCES.md`, `FRICTIONAL.md` | Credits; the honest log |

## What ran

All runs were made on 2026-11-09 by **Claude Code**, all **live** (no seeded runs in JS2), from this folder. Times are UTC.

| When | What | Result | Evidence |
|---|---|---|---|
| 08:00:21 | plain `curl` probes before any code | Klaviyo 200; Webflow on Greenhouse 200 with **0 jobs**; Webflow on Ashby 200 (508 KB); `klaviyoo` 404 | `evidence/probes/` |
| 08:01:08 | GATE.md v1 written (0 files in `agent/`) | — | `evidence/TIMELINE.md`, `evidence/GATE-v1-…md` |
| 08:01:42 | boundary predictions B1–B21 written (no `policy.py` yet) | — | `evidence/POLICY-predictions-2026-11-09.md` |
| 08:07:17 | tests + mutants, pre-patch | **53/53 OK**; mutants **9/10 KILLED, W1 STALE** (the code *was* W1) | `evidence/test-runs/…08-07-17Z…` |
| 08:07:29 | live, main watch list, pre-patch (baseline) | `incomplete` (3): `klaviyoo` 404, not retried, null; **webflow `ok`, 0** | `runs/2026-11-09T08-07-29Z-main-prepatch/` |
| 08:07:38 / 08:07:44 | live, wrong-answer list, pre-patch (baseline, then watch) | **`finished` (0)**, "webflow: 0 new". **Wrong** | `runs/wrong-answer-demo/` |
| ~08:08 | independent check of that run | **CONTRADICTED**: Ashby has 22 Webflow postings | `…prepatch-run2/independent-check.md` |
| 08:08:48 | review test against the pre-patch code | 3 FAIL, 1 ok | `review/test-before-patch.txt` |
| 08:08:54 / 08:09:03 | patch v1; tests rerun | 57/57 OK, 10/10 KILLED | `review/test-after-patch-v1.txt` |
| 08:09:13 | live, main list, v1 | `incomplete`; but the trace still says `outcome: ok` for Webflow → **revise** | `runs/…main-postpatch/`, `review/v1-trace-contradiction.txt` |
| 08:09:32 | 5th review test against v1 | FAIL (`['ok'] != ['empty']`) | `review/test-before-patch-v2.txt` |
| 08:09:42 / 08:09:52 | patch v2; tests rerun | 58/58 OK, 10/10 KILLED | `review/test-after-patch-v2.txt` |
| 08:10:05 | **live, main list, final code** (the trace in TRACE.md) | `incomplete` (3): webflow `empty_unverified`, klaviyoo 404 → null | `runs/2026-11-09T08-10-05Z-main-final/` |
| 08:10:08 | live, wrong-answer list, final code | `incomplete` (3) | `runs/wrong-answer-demo/…postpatch/` |
| 08:10:09 | live, DEMO budget (max_requests 3) | `budget_exhausted` (4); 3 boards not attempted | `runs/budget-demo/` |
| 08:10:20 | live, DEMO error list (typo board only) | `error` (5), ESCALATE | `runs/error-demo/` |
| ~08:10 | independent check of main-final | C1 6/6 OK, C2 6/6 OK, C3 webflow CONTRADICTED | `runs/…main-final/independent-check.md` |
| 08:10:20–08:10:59 | `tests/test_independent_check.py` written (2 of its 6 tests were wrong at first; the tests were fixed, not the checker); suite + mutants saved | **64 OK**; mutants "10/10" **INVALID** (runner bug: `verify/` not copied, found 08:2x) | `evidence/test-runs/2026-11-09T08-10-59Z-INVALID-mutants-runner-bug-suite-and-mutants.txt` |
| 08:11:14 | live DEMO: tried to force a real timeout (0.1 s) | **did not time out** (the request took 0.302 s; per-read timeout). The retry path is tested offline only | `runs/timeout-demo/` |
| 08:15:44 | **end-to-end check** (first; its output was not saved, see the 08:29:46 row): fresh copy of this folder in a temp dir; tests, mutants, live run, independent check | 64 OK; mutants 10/10 (invalid, see 08:21); `incomplete` (3); C3 webflow CONTRADICTED. Edge cases: `--out ../escape` → exit 5; unknown ATS / `../etc` slug → board error, no request; missing config → exit 5. **Bug:** two runs with the same label in the same second → exit 5 | temp copy (deleted); this table |
| 08:16 | bug fixed: a run that would collide gets a new `-2` folder; test rewritten with a fixed clock | 64 OK (mutant count invalid, same runner bug) | `review/later-fixes-after-review.diff` |
| 08:17–08:21 | **independent TA-style review** by a fresh subagent: **60/100 as it stood**; found the mutant-runner bug, a policy bypass on the state read, and 5 doc errors (see FRICTIONAL) | all fixed or disclosed | FRICTIONAL Part 2 |
| 08:21:17 | fixed runner (before the state-read fix) | 64 OK; control passed; **10/10 KILLED** (genuine); old copy list refused with CONTROL FAILED | `evidence/test-runs/2026-11-09T08-21-17Z-final-code-fixed-mutant-runner.txt` |
| 08:23:32 | **FINAL code** (state read through the policy, +1 test) | **65 OK**; control passed; **10/10 KILLED** | `evidence/test-runs/2026-11-09T08-23-32Z-FINAL.txt` |
| 08:23:37 | **live, main list, final code** | `incomplete` (3): same six answers as main-final; independent check (no probe): 1 contradiction (webflow reference 27) | `runs/2026-11-09T08-23-37Z-final-code/` |
| 08:24–08:30 | **second independent review** → request/read decisions traced, relative trace paths, mutant W10b added (it **survived** → test strengthened), doc errata | — | FRICTIONAL Part 2, GATE change log |
| 08:29:26 | **FINAL-2 code** | **66 OK**; control passed; **11/11 KILLED** | `evidence/test-runs/2026-11-09T08-29-26Z-FINAL-2.txt` |
| 08:29:32 | **live, main list, final code** (the trace in TRACE.md) | `incomplete` (3); every request, read and write decision traced; independent check: Webflow CONTRADICTED | `runs/2026-11-09T08-29-32Z-final/` |
| 08:29:46 | **end-to-end, saved**: fresh copy; tests, mutants, live run, independent check, 4 edge cases (outside `--out`, unknown ATS / `../` slug, missing config, same label twice → `-2` folder) | all as expected | `evidence/test-runs/2026-11-09T08-29-46Z-END-TO-END-fresh-copy.txt` |
| 2026-11-10 06:33:01 | **Omkar, his own terminal:** full suite + mutants | **66 OK**; **11/11 KILLED** | REVIEW-PACKET.md §5 |
| 2026-11-10 10:37–10:38 | **Omkar's drop rule** (second review): rule in GATE.md first, then `tests/test_drop_rule.py` vs. the unchanged loop, then the change | before: `FAILED (failures=5)`; after: **75 OK**; control passed; **14/14 KILLED** | REVIEW-PACKET.md "Second review"; `review/drop-rule/` |
| 2026-11-10 10:44:32–10:44:38 | **Omkar, his own terminal:** drop-rule tests vs. the old loop, full suite, mutants | `FAILED (failures=5)`; **75 OK**; `CONTROL passed`; **14/14 KILLED** | REVIEW-PACKET.md §S4 |
| 2026-11-10 10:38:43 | **live, main list, with the drop rule** | `incomplete` (3); no warnings; **9 real new postings** (HubSpot 5, Spotify 4), all `not_relevant`; independent check: Webflow CONTRADICTED again | `runs/2026-11-10T10-38-43Z-drop-rule-live/` |
| 2026-11-11 01:37 UTC (Nov 10, 20:37 ET) | **end-to-end 2, saved**, by Claude Code on a fresh copy: tests, mutants, live run, independent check, drop rule (`no_baseline` on a first run; `suspicious_drop` from a state edited in the temp copy only: 100 → 33), 4 edge cases | **75 OK**; control passed; **14/14 KILLED**; live `incomplete` (3) with **11 new postings**; Webflow CONTRADICTED; the edge cases gave exit 5 / no request sent / exit 5 / two folders | `evidence/test-runs/2026-11-11T01-37-19Z-END-TO-END-2-fresh-copy.txt` (script: `END-TO-END-2.sh`) |

## Sign-off: Job-Search Agent 2

**[Omkar]** This block is Omkar's. On 2026-11-10 Omkar wrote the "Not checked" list in his own words, replacing the six items Claude Code had drafted. "Not claiming" is still Claude Code's draft, which Omkar kept. "Checked" and "How" can only describe what he has done himself; he wrote them on 2026-11-10.

```text
Sign-off — Job-Search Agent 2
Checked:      I performed the full test suite and saw all 66 tests passing. I also
              performed mutant check and saw 11/11 KILLED. Moreover, I ran the review
              tests on both versions and saw four failures in the old loop and
              everything passed in the new loop. Finally, I opened the raw Webflow
              file and saw that it contains {"jobs":[]}.
How:          Claude Code wrote the code, tests, and docs. I ran the commands myself,
              read the review diff, and opened the raw Webflow file to check what it
              contained.
Not checked:  (my own list, Omkar, 2026-11-10; it replaces the six items Claude Code drafted)
              1. A real timeout or 5xx on a live server: the path shows only with a fake transport
                 (test_transient_failure_retries_at_most_twice). The socket timeout is per read,
                 not per request.
              2. A server that sends slowly, one byte at a time, can possibly keep a request past
                 90 sec. max_seconds is only checked between requests.
              3. After running, I didn't see a real suspicious_drop live. A board that shrinks
                 slowly over several runs is never flagged.
              4. Lever mapping met 4 real new Spotify postings, but I didn't check those verdicts
                 by hand. Ashby only tested on made-up data.
              5. Runs on two days only (2026-11-09 and 2026-11-10), started by hand, never on a
                 schedule.
Not claiming: The agent does not show that a board is complete or current: "0 new" means only that
              no id appeared that was not in the last run. A "relevant" verdict means the posting
              passed my JS1 rule, not that it is a good job. It never applies, emails, messages, or
              logs in, and nothing here tests that it would refuse an instruction to do so other
              than the policy's DENY on those actions and on non-GET requests (B7, B21).
Signed or withheld: Signed — Omkar Salian, 2026-11-10
```

## Driver's seat

**[Omkar]** The "Why that part stays mine" column must be in Omkar's own words. The other columns were written by Claude Code from the dated record.

| Part | What Claude should do | What I should do | Why that part stays mine | Evidence |
|---|---|---|---|---|
| **Loop: exits and budgets** | propose exits and budget numbers; implement and test them | decide the budget values and who may change them; confirm GATE.md | I decide what counts as a finished run and how much time and how many requests I'm willing to spend on it. | GATE.md "Omkar's decisions" (filled 2026-11-10); `config/budgets.json` |
| **Loop: watch list** | probe slugs, report traps (Webflow moved to Ashby; `hubspot` → 404) | decide which boards to watch, including whether to move Webflow to `ashby:webflow` | It's my job search, so I decide which companies I want to follow. | `evidence/probes/`, WRONG-ANSWER.md "Not done, on purpose" |
| **Loop: error policy and the deliberate failure** | classify failures; never invent a value | decide what escalates to me and when a retry is sound | I decide which errors I want to hear about and when it makes sense for the tool to try again. | `runs/…main-final/trace.jsonl` (404 → one attempt, null) |
| **Permission policy** | write the boundary cases and the code; predict before coding | confirm the allow-list and the never-do list; run the boundary tests myself | Applying, emailing, or logging in would happen in my name, so I decide whether the tool can do any of those things. | POLICY.md; `evidence/POLICY-predictions-…md` |
| **Review: test and patch** | reproduce the defect, write the test before the patch, write the patch | read the diff as behavior; rerun the old-code check myself | If the change is wrong, I'm responsible for approving it. I need to understand what the test checks and how the patch changes what the program does. | REVIEW-PACKET.md §2–§5; `review/` |
| **Review: decision** | recommend, with evidence | **accept / revise / reject** | As the reviewer, I'm the one who decides whether the evidence is enough to accept the change. | REVIEW-PACKET.md §6 |
| **Sign-off** | list the true gaps | choose what I checked, and sign or withhold | My signature, and I vouch for what I did. | this README |
