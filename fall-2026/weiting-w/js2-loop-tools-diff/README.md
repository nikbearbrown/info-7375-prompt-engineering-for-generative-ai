# INFO 7375 — Job-Search Agent 2: The Loop, the Tools, and the Diff

Weiting W. (`fall-2026/weiting-w`)

**Layer 2 of my own JS1 agent.** The base is
[`fall-2026/weiting-w/js1-contract-and-watch/`](../js1-contract-and-watch/) in
this repository, commit `bcc40d7e96e1374a1083fd1bb8a7a0bd6431061d` — one board,
one written contract, one rule. This layer adds a bounded loop over several
boards across three applicant-tracking systems, a permission policy enforced in
code, an independent cross-check for the failure the loop cannot see, and a
review of a change to the rule JS1 wrote. `SOURCES.md` says which files came
across unchanged, which changed, and which were deliberately left behind.

## Language and toolchain

- **Python 3**, standard library only, for the agent and both tools. No HTTP
  client library, no scraping library, no headless browser, no model.
- **pytest** for the tests — the only dependency, in `requirements-dev.txt`.
- Developed against Python 3.13.16 in a Linux container; the live run was on
  macOS with python.org Python 3.14 and pytest 9.2.0. No version-specific
  features are used; the standard library calls are long-stable.

## The gate came first

`GATE.md` was committed **alone**, before any agent code existed, in
`ce94b1f`. That ordering is the point and it is checkable:

```
git log --oneline --reverse -- fall-2026/weiting-w/js2-loop-tools-diff
git show --stat ce94b1f
```

`ce94b1f` contains `GATE.md` and `.gitignore` and nothing else. It fixes the
four loop exits, the budgets, the repeat rule, the error policy by exception
class, the permission policy, the 19 boundary-case predictions, the
finished-wrong-answer problem, and the four wrong versions — all before there
was code to make any of them convenient. Every change since is an amendment in
`GATE.md` §8, dated, with a reason, and three of them record places the frozen
document was wrong.

## Running it

```
cd js2-loop-tools-diff
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
```

The live loop, which makes one GET per board to four real public job boards:

```
python3 -m agent watch
python3 tools/crosscheck.py
```

`watch` exits **1**, and that is correct: the plan contains a board that is
broken on purpose, so the run exits `incomplete`. On macOS, python.org builds
need `SSL_CERT_FILE=$(python3 -m certifi) python3 -m agent watch` — see
Troubleshooting.

**Reproducing any run in here without network access**, which is how a TA should
read this repository:

```
python3 -m agent watch --boards config/boards-wronganswer.json \
  --replay-from evidence/seeded/replay-wrong-answer \
  --raw-dir evidence/seeded/wrong-answer --runs-dir evidence/seeded/runs \
  --state evidence/seeded/state/seen.json

python3 tools/crosscheck.py --raw-dir evidence/seeded/wrong-answer \
  --boards config/boards-wronganswer.json --state evidence/seeded/state/seen.json

python3 tools/boundary_table.py --check
```

Every run report records `mode`, so a replay can never be mistaken for a live
fetch. There is deliberately **no flag that widens a budget or an allow-list**:
`GATE.md` §2 says a budget changes only by a written decision, and a limit any
caller can raise is not a limit.

## What is in here

| path | what it is |
|---|---|
| `GATE.md` | the frozen gate, plus three amendments |
| `agent/` | the loop, the policy, the trace, the three provider adapters, the rule |
| `tools/crosscheck.py` | the independent check — never reads a run report |
| `tools/boundary_table.py` | generates `reports/boundary-tests.md` by running the real policy |
| `tools/make_rv2_baseline.py` | records JS1's R-v2 verdicts, run once |
| `review/review-packet.md` | the Chapter 6 review of amendment A2 |
| `reports/wrong-answer.md` | the finished wrong answer, demonstrated and caught |
| `reports/boundary-tests.md` | 19 predicted vs 19 actual, generated |
| `evidence/PROVENANCE.md` | the origin of every byte under `evidence/` |
| `SOURCES.md` | what came from JS1; what Claude contributed |
| `FRICTIONAL.md` | what fought back, and what is still broken |

## The review packet, in three commits

The ordering is the deliverable, so it is in git rather than in prose:

| commit | what |
|---|---|
| `3a0896f` | the defect reproduced by a test, **committed red**. Output kept in `review/before-patch-failure.txt`: 8 failed, 3 passed. |
| `7bf3d11` | the patch. R-v2a → R-v3. |
| `250dff8` | the review: scope checked against the claim made in advance, decision, and one case the test still misses. |

`git diff 3a0896f..7bf3d11 -- tests/test_review_g4_location.py` is **0 lines**.
The same test file that produced 8 failures produced 11 passes with not one
character changed by the patch. That is the check that the green report was
earned rather than arranged.

The review step afterwards added 70 lines to that file and removed none —
`git diff 7bf3d11..HEAD -- tests/test_review_g4_location.py | grep '^-[^-]'` is
empty — because the review's own finding (§7 of the packet) is recorded there as
a strict-xfail test. Quoting the range as `3a0896f..HEAD` would have been the
easier sentence and would have been false; the ranges are split so each claim
can be checked on its own.

The same discipline, used twice more: `12390f4` (red) → `d6013a8` closed the
write-policy gap described in `FRICTIONAL.md` §2.

## What I ran myself

Everything under `evidence/raw/`, `evidence/runs/` and `evidence/state/` was
produced by me, on my own Mac, in my own Terminal, on **2026-11-11T00:18Z**
(2026-11-10, 7:18pm ET). Claude's cloud container cannot reach any of the three
applicant-tracking hosts, and neither can the Linux VM that bridges to my
machine — `FRICTIONAL.md` §8 has the detail. macOS, python.org Python 3.14,
pytest 9.2.0.

```
cd ~/Downloads/js2-final
python3 -m pytest -q
SSL_CERT_FILE=$(python3 -m certifi) python3 -m agent watch
python3 tools/crosscheck.py
python3 tools/boundary_table.py --check
```

```
104 passed, 2 xfailed, 1 warning in 0.29s

[INCOMPLETE] complete=False  mode=live  loop=L-v1  rule=R-v3
  boards planned=5 attempted=5 observed=4 failed=1
  requests 5/12   seconds 1.734/90.0
  ok        greenhouse:reddit            postings=157  attempts=1
  ok        lever:spotify                postings=85  attempts=1
  ok        ashby:ramp                   postings=177  attempts=1
  ok        ashby:linear                 postings=33  attempts=1
  permanent greenhouse:js2-no-such-board-9f3a DELIBERATE  attempts=1  PermanentFailure: HTTP 404 from https://boards-api.greenhouse.io/v1/boards/js2-no-such-board-9f3a/jobs
  first run: every posting recorded as seen, none reported as new.

  ESCALATE: exit=incomplete complete=False. failed boards: greenhouse:js2-no-such-board-9f3a (permanent). The posting list above is NOT complete.

  run report: evidence/runs/run-20261111T001812Z.json
  trace:      evidence/runs/trace-20261111T001811Z.jsonl

crosscheck: reading evidence/raw (never the run report)

board                           latest  previous  floor  state  flags
ashby-linear                        33      None      1     33  -
ashby-ramp                         177      None      1    177  -
greenhouse-reddit                  157      None      1    157  -
lever-spotify                       85      None      1     85  -

crosscheck: nothing flagged.

all 19 boundary cases match the predictions in GATE.md §5.5
```

**Four boards across three applicant-tracking systems**, 452 postings, one GET
each. **The fifth board failed on purpose**, and it failed the way `GATE.md` §4
said it would, which is the part I care about:

| predicted in `config/boards.json`, before running | what happened |
|---|---|
| classification `permanent` | `permanent` |
| zero retries | `attempts=1` |
| reported as failed with **no count** | `postings_seen: null`, not `0` |
| the run exits `incomplete` | `[INCOMPLETE] complete=False` |
| the other four boards still produce their postings | 157, 85, 177, 33 |

`watch` exits **1**. It did not quietly succeed, and it did not fold the dead
board into the summary as a zero — folding it in is wrong version W1, and
`tests/test_loop_exits.py` is what stops it.

**The cross-check flagged nothing**, and that is the correct result here: it was
the first run, so every board's `previous` is `None` and only the hand-written
floor of 1 could fire, which 33, 85, 157 and 177 all clear. A tool that only
ever fires is not a check — `reports/wrong-answer.md` is the run where it does
fire, four times, on a board the loop called `finished`.

### A note on which code produced this

I ran this twice. The first run (2026-11-11T00:12Z) used a copy of the code
taken before the last three commits, so the evidence in this repository would
have been produced by a version that is not the version submitted. Replaying
those four captured responses under the current code gave identical counts and
an identical exit status, so nothing observable had changed — but rather than
explain that in a provenance note, I re-ran from a clean copy of the submitted
code. **The evidence here is from that second run.** The first run's files are
not in this repository.


## Sign-off — Job-Search Agent 2

**Checked** — which properties, by which of my own tests:

1. *The gate was written before the code.* `git show --stat ce94b1f` is two
   files, `GATE.md` and `.gitignore`, and nothing else.
2. *The permission policy decides the 19 cases the way §5.5 predicted.*
   `tests/test_policy_boundaries.py` (25 tests) and
   `python3 tools/boundary_table.py --check`, which recomputes the table by
   calling the real `Policy` rather than reprinting predictions.
3. *A failed board never becomes a zero.* `tests/test_loop_exits.py` —
   `test_a_failed_board_never_appears_as_zero_new` and
   `test_exit_status_is_derived_not_asserted`, both of which also run against
   wrong version W1 and are asserted to catch it.
4. *Amendment A2 moves exactly 2 of JS1's 163 real verdicts and no others.*
   `tests/test_rule_carried_over.py` —
   `test_rv3_moves_exactly_the_verdicts_the_amendment_claimed` and
   `test_the_other_161_verdicts_are_untouched`.
5. *The loop exits `finished` on an empty board and an independent check catches
   it anyway.* `tests/test_wrong_answer.py` (9 tests), including
   `test_the_crosscheck_reaches_its_verdict_with_no_run_report_on_disk`, which
   deletes every run report and trace from disk first.
6. *Every file the agent writes goes through the policy.*
   `tests/test_all_writes_go_through_the_policy.py`, including a test that reads
   `agent/*.py` for write primitives and fails on a module that never mentions
   `check_write`.
7. *The agent calls no model, reads no environment variable, and imports nothing
   that could send or log in.* `tests/test_no_model_and_no_environment.py`.
8. *The deliberate failure behaves as `config/boards.json` predicted.* The live
   run of 2026-11-11T00:18Z, above: `permanent`, `attempts=1`,
   `postings_seen: null`, exit `incomplete`.

**How** — by which means, honestly split:

- *By a test written before the code it tests:* items 1–2 (the 19 predictions
  were frozen in `GATE.md` before `agent/` existed) and the two red-first
  sequences — `3a0896f` (the G4 defect, 8 failed) → `7bf3d11` (the patch), and
  `12390f4` (the write-policy gap, 4 failed) → `d6013a8` (the fix). Both
  failure outputs are kept verbatim in `review/`.
- *By recomputation:* item 4. R-v3 is recomputed over JS1's 163 real postings
  and compared against the verdicts JS1's own committed R-v2 produced, every
  time the suite runs.
- *By hand, by me:* item 8, and the live run of the whole loop on my own Mac —
  `pytest -q`, `agent watch`, `crosscheck.py`, `boundary_table.py --check`,
  output above. Also the decision in `review/review-packet.md` §7, and the
  choice to keep all eight "Not checked" entries below rather than fix the
  easy ones.
- *With Claude's help:* everything else. Claude (Opus 5) wrote `GATE.md`, all
  of `agent/`, `tools/` and `tests/`, and the reports. It also found three of
  the defects listed below against its own work without being asked —
  `FRICTIONAL.md` §2, §3b and `review/review-packet.md` §3. I did not write the
  code and I am not claiming to have.

**Not checked** — eight, and these are real:

1. **R-v3 is validated on one board's data.** All 163 postings in the baseline
   are Greenhouse, one company, overwhelmingly US locations. G4's behaviour on
   Lever's and Ashby's location shapes is covered only by constructed cases. I
   have never judged a real Lever or Ashby location string.
2. **The review's own test cannot see the defect class it was written about.**
   Its oracle uses the same substring comparison G4 uses, so it confirms only
   that G4 agrees with itself. `Boston, Lincolnshire, United Kingdom` is still
   judged relevant. Recorded as a strict-xfail test; reasoning in
   `review/review-packet.md` §7.
3. **The state file's `last_count` regresses silently.** It went 163 → 0 during
   the wrong-answer demonstration and the loop said nothing. The cross-check
   does not trust it, which contains the damage but does not repair it
   (`FRICTIONAL.md` §5).
4. **Two runs in the same wall-clock second cannot both save a response.** The
   second refuses with `NeedsApproval` rather than overwriting. Safe direction,
   still a defect (`FRICTIONAL.md` §4).
5. **The JS1 labels this submission's baseline leans on were not blind.** JS1
   recorded that I had been told R-v2's verdicts before deciding the four rows
   I labelled myself, two of which are the postings under review. I disagreed
   with the agent on all four, which is the opposite of what anchoring would
   produce, but no number here is an independent human comparison.
6. **The G1 seniority defect is still present**, carried over from JS1 and
   asserted still-present by a test so it cannot drift out of the record.
7. **The cross-check is a command, not a step.** Nothing runs it automatically.
   A nightly job that ran the loop and not the cross-check would receive the
   honest wrong answer every morning.
8. **The boundary table is the cases I thought of.** It passed 19 of 19 while
   three of the four writers bypassed the policy entirely. Its completeness is
   not evidence of the policy's.

**Not claiming** — what this agent does not show:

- **It does not show that the agent finds good jobs.** This submission reports
  no precision or recall. The only human labels in existence are JS1's 25 rows,
  and they were not blind (above). Every count here is a count of what the
  boards returned, never of whether a judgement about them was right.
- **The live run left no rule verdicts behind at all**, which I did not notice
  until I went to check the sentence above. `agent/cli.py` judges every posting
  it considers new, and on a first run *every* posting is new — so R-v3 ran over
  all 452 — but the report then writes `new_postings: 0` and `entries: []`
  because announcing 452 "new" postings on a first run is noise. The work was
  done and discarded: `evidence/runs/run-20261111T001812Z.json` contains no
  verdict. So the live run demonstrates the **loop**, the budget, the error
  policy and the policy enforcement, and it demonstrates nothing about the rule.
  Every claim about R-v3 in this submission rests instead on JS1's 163-posting
  capture, where the verdicts are recomputed by
  `tests/test_rule_carried_over.py` and can be checked. A second run against
  these boards would produce verdicts; there has not been one.
- **It does not show that the boards were read correctly, only that they
  parsed.** 157, 85, 177 and 33 are what the adapters produced. I did not open
  the four companies' career pages and count.
- **It does not show the policy is complete.** It shows the policy decides 19
  predicted cases correctly and that four writers now ask it. An attack nobody
  predicted is not in the table.
- **It does not show that one run proves anything about reliability.** The loop
  ran once, live, on a good network, with no retry exercised — the retry and
  backoff paths are covered only by constructed failures in the suite.
- **It does not show that Claude's patch was correct beyond the property I
  tested.** I accepted a diff; I did not formally verify it.
- **It is not a system anyone should job-hunt with.** It watches, it judges by a
  crude written rule, and it has three known unfixed defects listed above.

**Signed:** Weiting Wang — 2026-11-10

## Driver's seat

| decision | mine | Claude's | how to tell |
|---|---|---|---|
| Build layer 2 on my own JS1 rather than a new codebase | ✅ | | `SOURCES.md`; the carried-over files are byte-identical |
| Which defect the review packet is about (the G4 remote false positive) | ✅ | | it is a defect JS1 pre-registered and that I labelled against |
| The four loop exits, budgets, error classes, permission policy | | ✅ | written in `GATE.md`, which Claude wrote |
| The budget numbers (6 boards, 12 requests, 90s, 2 retries) | | ✅ | `config/budget.json` carries the sizing rationale |
| All implementation code, tools and tests | | ✅ | stated plainly in `SOURCES.md` |
| The G4 patch, and widening it to make `remote_ok` reject | | ✅ | `review/review-packet.md` §3 row 2 |
| **Accepting** that patch, and not fixing the defect its review found | ✅ | | `review/review-packet.md` §7 |
| Every real byte in `evidence/raw/` | ✅ | | Claude's container and the bridge VM cannot reach any board host; `FRICTIONAL.md` §8 |
| The four JS1 labels the baseline rests on | ✅ | | with the non-blindness JS1 recorded, repeated here |
| Finding that `GATE.md` §5 was false | | ✅ | `FRICTIONAL.md` §2; Claude reported it against its own work unasked |
| What goes in this sign-off's "Not checked" list | ✅ | | I chose to keep all eight |

## Troubleshooting

**`CERTIFICATE_VERIFY_FAILED` on macOS.** python.org Python ships without the
system trust store wired up:

```
python3 -m pip install certifi
SSL_CERT_FILE=$(python3 -m certifi) python3 -m agent watch
```

`SSL_CERT_FILE=…` prefixes **one** command. A later bare `python3 -m agent watch`
will fail again.

**`python3 -m agent watch` exits 1.** Expected. One board in the plan is broken
on purpose, so the run exits `incomplete`.

**`python3 -m agent.cli` does nothing.** The entry point is `python3 -m agent`.
The `.cli` form used to exit 0 in silence; it now runs, but `python3 -m agent`
is the one in every command above.

**pytest collects another student's files.** Run it from inside
`js2-loop-tools-diff/`, not from the repository root.
