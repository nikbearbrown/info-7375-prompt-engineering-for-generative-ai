# Job-Search Agent 2: The Loop, the Tools, and the Diff

**Student:** Shreyash Yadav (`shreyash-y`) · INFO 7375 Prompt Engineering & Agentic AI, Fall 2026 · Professor Nik Bear Brown
**Assignment:** JS2, Chapters 4–6 · due 2026-11-10

**Starting point:** my own JS1 agent (`fall-2026/shreyash-y/js1-contract-and-watch`, submitted commit `bb193d9`). Its posting reader, rule v1, persona and validator were copied in unchanged in commit `4213c8c`. Neither the Reallocation Engine nor Lectern was used.

*Everything below the summary was drafted by Claude Code and checked against the files. The summary, GATE.md, the decisions in `review/` and the signature are Shreyash's.*

## For the grader: where each rubric item is, and one command to check it

Run every command from this folder.

| Rubric item | Where | Check it |
|---|---|---|
| GATE written first: exits, budgets, repeat rule, error policy, permissions, wrong versions | [GATE.md](GATE.md) | `git show --stat 9fbab0d` holds GATE.md only |
| Loop: 6 boards on 3 systems, budgets, exits, a record of every observation | [TRACE.md](TRACE.md), `runs/*/trace.jsonl` | `python3 -m unittest tests.test_loop -v` |
| Deliberate failure handled without inventing a value | TRACE.md, run 1 lines 14–19 | `sed -n 14,19p runs/20261110T002501Z/trace.jsonl` |
| Finished wrong answer caught by an independent check | TRACE.md, last section | `python3 jsagent/check.py runs/seeded-finished-wrong/finished-wrong-SEEDED` |
| Permission policy in code, 22 predicted boundary cases | [BOUNDARY-TESTS.md](BOUNDARY-TESTS.md) | `python3 -m unittest tests.test_policy tests.test_policy_symlink tests.test_policy_nested_symlink -v` |
| Review packet: reproduce, test first, diff as behavior, scope, my commands, my decision, missed cases | [REVIEW-PACKET.md](REVIEW-PACKET.md), opening with my own reading of the diffs | `git log --oneline 6f4ae08^..ba0a5b0` |
| Sign-off and driver's seat | the end of this README | — |
| Two gaps an independent regrade found on 2026-11-10 (CLI reads skipped the read rule; an empty board list said `finished`), tests committed failing before the fix | `tests/test_regrade_gaps.py`, `evidence/regrade-gaps-*` | `python3 -m unittest tests.test_regrade_gaps -v` |
| Three gaps a second regrade found on 2026-11-10 (`--runs-dir runs-evil` was allowed, GATE.md wrong version 3; a posting with no id crashed the run; the check trusted the summary), tests committed failing before the fix | `tests/test_regrade2_gaps.py`, `evidence/regrade2-gaps-*` | `python3 -m unittest tests.test_regrade2_gaps -v` |
| Gaps a third regrade found on 2026-11-10 (a bad or missing board token, a cut-off body or SSL error, and a corrupt state file crashed the run; the check never compared raw files with their recorded sha256), tests committed failing before the fix | `tests/test_regrade3_gaps.py`, `evidence/regrade3-gaps-*` | `python3 -m unittest tests.test_regrade3_gaps -v` |
| All tests; the 19 frozen test and fixture files match their recorded hashes (two disclosed changes) | `tests/`, `tests.frozen.sha256` | `python3 -m unittest discover -s tests -t . && shasum -a 256 -c tests.frozen.sha256` |

## Summary, in my own words

*Shreyash's words, typed into the session on 2026-11-10, replacing the earlier versions (the 2026-11-09 summary predated run 3). Claude Code did not change them.*

The agent checks six boards across three applicant-tracking systems: Greenhouse (Oscar, Klaviyo), Ashby (Linear), and Lever (Palantir, WHOOP, and the deliberate 404 board). All three recorded live runs ended `incomplete` because the failed board was handled according to the error policy without inventing a posting count. Run 1 established the baseline, Run 2 found zero new postings, and Run 3 identified six new postings, all classified as Not Relevant. The finished-wrong demonstration showed that a run can report `finished` despite receiving incomplete data; an independent checker detected the discrepancy. The review packet showed that passing tests did not guarantee correct behavior: revision 1 passed all 84 tests but misread perks in 16 postings, so I sent it back for revision and later accepted revision 3 with documented limitations.

## Language and toolchain

- **Python 3**, standard library only, with nothing to install. Tested only on Python 3.14.6 (macOS); the code uses 3.9+ syntax.
- **Tests:** `unittest`.
- **Network:** only the three hosts in GATE.md section 6, and only in a live `run`. Every other command here runs offline.
- No model is called anywhere in JS2.

## Commands, from a fresh clone

```bash
git clone -b shreyash-y/js2-loop-tools-diff https://github.com/shreyashyadav1/info-7375-prompt-engineering-for-generative-ai.git
```

```bash
cd info-7375-prompt-engineering-for-generative-ai/fall-2026/shreyash-y/js2-loop-tools-diff
```

All tests, offline (121; one is an expected failure, Shreyash's Physician Reviewer test):

```bash
python3 -m unittest discover -s tests -t . -v
```

Check the 19 frozen test and fixture files against their recorded hashes. Two were changed openly after their first run (`review/08`, BOUNDARY-TESTS row 21); `test_rule.py`, copied from JS1, is not frozen:

```bash
shasum -a 256 -c tests.frozen.sha256
```

Only the 20 predicted permission boundary cases:

```bash
python3 -m unittest tests.test_policy -v
```

A live run of all six boards in `boards.json`. It writes a new `runs/<UTC time>/`; exit codes are 0 finished, 2 incomplete, 3 budget-exhausted, 4 error:

```bash
python3 -m jsagent run
```

The independent check on any saved run:

```bash
python3 jsagent/check.py runs/20261110T002501Z
```

The **seeded** finished-wrong-answer demo, offline. It writes into a fresh `runs/seeded-finished-wrong/`, so move the committed one aside first:

```bash
mv runs/seeded-finished-wrong /tmp/seeded-finished-wrong-committed && PYTHONPATH=. python3 demo/make_finished_wrong.py runs/20261110T002501Z && python3 -m jsagent run --boards demo/boards-four-good.json --runs-dir runs/seeded-finished-wrong --replay runs/seeded-finished-wrong/input/map.json --run-id finished-wrong; python3 jsagent/check.py runs/seeded-finished-wrong/finished-wrong-SEEDED
```

## What ran

| When (EST) | What | Result | Evidence |
|---|---|---|---|
| 2026-11-09 19:22 | Tests run before any new code | 3 new test modules fail to import | `evidence/tests-before-new-code-2026-11-09.txt` |
| 2026-11-09 19:24 | Mutation check: break the code the way each wrong version would | 5 of 6 caught; the symlink-refusal line is untested on its own | `evidence/mutation-check-2026-11-09.txt` |
| 2026-11-09 19:25 | **Live run 1**: 6 boards, Greenhouse + Ashby + Lever | `incomplete`: 4 ok (199/150/32/304), the deliberate 404 failed after 1 request, WHOOP flagged `empty`; 6/12 requests, 3.4 s; check: no findings | [TRACE.md](TRACE.md) |
| 2026-11-09 20:17 | **Live run 2**, the same six boards | `incomplete` again; read run 1's state, so no baselines; 0 new on all four ok boards; all six responses byte-identical to run 1's (recount); check: no findings | [TRACE.md](TRACE.md), `evidence/run2-recount-2026-11-09.txt` |
| 2026-11-10 15:47 | **Live run 3**, a day later | `incomplete`; **6 real new postings** (2 Oscar, 1 Linear, 3 Palantir) judged in the loop by rule v2 rev 3, all Not Relevant. Closest calls: Palantir SWE intern postings failing only department (`Dev`) and location. Recount matches; check: no findings | [TRACE.md](TRACE.md), `evidence/run3-recount-2026-11-10.txt` |
| 2026-11-09 | **Seeded finished wrong answer** | the agent says `finished`; the independent check flags `meta.total 199` vs 20 and 179 postings gone | [TRACE.md](TRACE.md), `evidence/finished-wrong-SEEDED-2026-11-09.txt` |
| 2026-11-09 | Boundary tests | 20 of 20 as predicted | [BOUNDARY-TESTS.md](BOUNDARY-TESTS.md) |
| 2026-11-10 | Boundary row 21 (after review): a symlink inside runs/ to a new file inside runs/ | as predicted; with the no-symlink line deleted it now fails, which closes the mutation-check gap | `evidence/boundary-row21-run-2026-11-10.txt` |
| 2026-11-10 20:29–20:31 | Regrade gaps: CLI reads, empty board list | 5 tests committed failing (`01aaeb2`), all 5 pass after the fix; full suite 105, OK; the three live runs still give no findings | `evidence/regrade-gaps-before-fix-2026-11-10.txt`, `evidence/regrade-gaps-after-fix-2026-11-10.txt` |
| 2026-11-10 20:44–20:46 | Second regrade gaps: write root, malformed posting, check vs trace | 8 of 10 tests committed failing (`ebfd405`), all 10 pass after the fix; full suite 115, OK; `--runs-dir runs-evil` now stops with exit 4; the live runs still give no findings and the seeded run is still caught | `evidence/regrade2-gaps-before-fix-2026-11-10.txt`, `evidence/regrade2-gaps-after-fix-2026-11-10.txt` |
| 2026-11-10 21:01–21:03 | Third regrade gaps: bad board entries, cut-off bodies, corrupt state, raw-file hashes | 6 of 6 tests committed failing (`c31cfc2`), all pass after the fix; full suite 121, OK; the live runs still give no findings and the seeded run is still caught | `evidence/regrade3-gaps-before-fix-2026-11-10.txt`, `evidence/regrade3-gaps-after-fix-2026-11-10.txt` |
| 2026-11-09 19:26–19:45 | Review packet: rule v2, three revisions | rev 1 revise, rev 2 rejected on reading, rev 3 accepted with known limitations | [REVIEW-PACKET.md](REVIEW-PACKET.md) |

## Known limitations of the loop and the permission policy

- **The time budget is enforced at request boundaries, not as a strict wall-clock deadline, and tested only with a constructed clock.** A server that keeps sending data slowly can hold one request past the limit, because the HTTP timeout applies to each wait, not to the whole response (GATE-NOTES, in Shreyash's words; found by the third regrade). Until 2026-11-10 the 120-second limit was checked only before each request, so one slow request could run about 20 s past it. A test written first (`tests/test_loop_deadline.py`, commit `325e98c6`, failing: "20 not less than or equal to 10") was followed by the fix: each request now gets the smaller of 20 s and the time left, and no request starts with 0 s left. The three live runs (3.4–7.8 s) were made before this change and never came near the limit, and no real slow request has been seen.
- **Two gaps fixed on 2026-11-10, after an independent regrade.** (1) The command line read `--boards`, the `--replay` map and the replay's saved responses directly, not through `Files.read`, so a path outside this folder was accepted even though GATE-NOTES says reads stay inside it. They now go through `Files.read` and are refused. (2) An empty board list ran as `finished` with nothing checked, and the check said "no findings": a finished wrong answer neither caught. The loop now exits `error`, and the check flags any `finished` run with no board checked. Tests first: `tests/test_regrade_gaps.py`, failing in `01aaeb2`. `budgets.json`, `GATE.md` and the persona are still read directly, at fixed paths inside this folder. The three live runs were made before this change.
- **Three more gaps fixed on 2026-11-10, after a second regrade.** (1) `--runs-dir` set the write root to any folder, so `--runs-dir runs-evil` wrote into `runs-evil/`: GATE.md's wrong version 3, reached through the command line while the 22 rows only tested the `Files` class. Now the root must be `runs/` or a folder inside it. (2) A posting with no `id` crashed the run with a `KeyError`, ending in none of the four exits. Now it fails that board as `bad-shape` and the run ends `incomplete`. A refused read, write or overwrite now stops `python3 -m jsagent` with exit 4 and one line, not a traceback; when the refused write is the run's own record, no summary can be written. (3) The check trusted the summary. Now it compares the summary with the trace (boards at start, exit at the end) and recounts new postings from the raw ids and the previous state. Tests first: `tests/test_regrade2_gaps.py`, failing in `ebfd405`. The check still reads the saved files only, so a run that rewrote its trace and summary together would not be caught.
- **Four more gaps fixed on 2026-11-10, after a third regrade.** A board entry with a bad token or no token now fails that board as `bad-config` and the run goes on (GATE.md section 5). A body cut off mid-read, an SSL failure or another OS-level network error is now a `network` failure for that board. A state file that cannot be read ends the run as `error`, with its exit line. And the check now compares each raw file with the sha256 the trace recorded when it was saved. Tests first: `tests/test_regrade3_gaps.py`, failing in `c31cfc2`. Still not caught: a partial Ashby, Lever or Greenhouse-without-`meta` response that keeps more than half the postings, and a run that rewrote its trace too.
- **Check, then write.** The path is resolved and checked, then opened. A folder swapped for a symlink in between could be followed. This is not tested and not closed (BOUNDARY-TESTS.md, "What these 22 rows do not cover"). Hard links are not detected either.

## Known limitations of the filtering rule

The rule is **not** correct in general. Rule v2 revision 3 was accepted with these open, and they stay open:

- **An office tag beats the ad.** Oscar's *Physician Reviewer – Utilization Management* carries the office "Remote (Arizona)", but its ad says "reside in the United States". The rule trusts the tag and fails condition 3. That verdict is still Not Relevant on other grounds, but a software job written the same way would be wrongly rejected. **Not fixed, but now tested:** `tests/test_shreyash_physician_reviewer.py`, whose expectation Shreyash wrote, runs it on the real posting as an *expected failure*.
- **Location field against office list.** Some Klaviyo postings list location "San Francisco, CA" with the office "Boston". The rule reads the location field only, and which one should win has not been decided.
- **Department labels.** Palantir's Lever department `Dev` is not on the contract's department list, so its "Software Engineer, Intern" postings fail condition 2. **Decided on 2026-11-10, not built** (`review/19`): count `Dev` as engineering for Palantir only, through a documented provider-specific reading, never for every board. Those postings would still fail on location.
- **One hand label was wrong.** On Klaviyo 7809608003, Shreyash's JS1 hand label left out condition 4. The ad names only one of Alex's skills, Python, so the rule's skills failure is right (`review/19`). The "19 of 20" against the hand labels is really 20 of 20 on the corrected label; the label itself is left as it was committed in JS1.
- **Phrasings not seen yet.** Experience and remote are read with patterns learned from 685 postings. "Several years", or a preferred heading the cue list does not know, would be misread.
- **The independent check cannot see partial Ashby or Lever responses**, because neither reports a total.

## Folder map

- `GATE.md` (Shreyash's), `GATE-NOTES.md` (how it became code), `budgets.json`, `boards.json`
- `jsagent/`:
  - `policy.py`: hosts and paths, the permission policy in code.
  - `providers.py`: Greenhouse, Ashby and Lever.
  - `transport.py`: live HTTP, and replay for seeded runs.
  - `loop.py`: exits, budgets, repeat rule, error policy, trace.
  - `check.py`: the independent check. It imports nothing from the agent.
  - `rule.py`: rule v2 rev 3.
  - Also `posting.py`, `persona.py`, `validator.py`, copied from JS1.
- `tests/`, `tests.frozen.sha256`, `BOUNDARY-TESTS.md`
- `runs/`:
  - `20261110T002501Z/`: live run 1, with its raw responses, trace and summary.
  - `20261110T011708Z/`: live run 2.
  - `20261110T204749Z/`: live run 3, the 6 new postings.
  - `state/`: one new state file per run.
  - `seeded-finished-wrong/`: SEEDED.
- `review/`: every step of the review packet in order, with Shreyash's own runs and decisions. `REVIEW-PACKET.md` reads them in order.
- `evidence/`, `demo/`, `persona/` (fictional Alex Morgan, from JS1)

## Sign-off — Job-Search Agent 2

*Drafted by Claude Code. Shreyash checked it, accepted the two 2026-11-10 changes (row 21 moved to Checked; the Palantir `Dev` department kept under Not checked), and signed it in the session on 2026-11-10. Lines were added afterwards the same day (the `Dev` decision, rows 21–22, the deadline test, Shreyash's own test, the check-then-write race), the first sentence of "Not claiming" is Shreyash's wording, and so is the end of "How" from "I initially verified" (typed in after the regrades); Shreyash re-read the whole sign-off and kept the signature on 2026-11-10.*

```text
Checked:      - Exits, budgets, repeat rule and error policy: tests/test_loop.py (the five GATE.md
                wrong versions written as code and caught; 404 tried once; timeout/5xx once; budgets
                count retries); in live run 1 the deliberate 404 and the empty board were handled
                as GATE.md says (TRACE.md lines 14-19).
              - Permission policy in code: tests/test_policy.py, 20 cases predicted in
                BOUNDARY-TESTS.md before policy.py existed, 20 of 20 as predicted; row 21
                (tests/test_policy_symlink.py, added after review) covers the no-symlink line,
                which the mutation check had shown no test covered; row 22 covers a chain of
                symlinks (tests/test_policy_nested_symlink.py).
              - The time budget as a deadline: tests/test_loop_deadline.py, committed failing
                before the loop change (325e98c6), passing after.
              - My own test: tests/test_shreyash_physician_reviewer.py. I wrote the expectation
                (condition 3 should pass, because the ad says "reside in the United States", and
                the verdict must still follow the other conditions). Claude Code wrote the code.
                It runs as an expected failure until the rule is fixed.
              - Six real new postings in live run 3, judged in the loop and recounted from the raw
                files (evidence/run3-recount-2026-11-10.txt).
              - A finished wrong answer caught by a check that does not use the agent's code:
                tests/test_check.py and the seeded demo.
              - Rule v2 rev 3: tests/test_rule_v2*.py on real postings, plus my own runs of the
                tests and the behavior diff (review/04, review/17).
How:          The tests were written by Claude Code from GATE.md and committed before the code
              (cef009e before f4b553d; 6f4ae08 before the rule patch). I ran the review commands
              myself. The behavior diffs are recomputations over the 685 saved postings. The
              decisions in review/05 and review/18 are mine. On 2026-11-10 I re-ran the full suite
              (OK) and confirmed row 21's prediction was in 2b8ed44 before any result
              (evidence/commands-run-by-shreyash-2026-11-10.txt). I initially verified 12 frozen
              test hashes and later verified 17 after the additional changes. The current submission
              contains 18 frozen files, but I am not claiming to have personally checked all 18
              unless I run that verification myself. The automated verification results are recorded
              separately (evidence/automated-verification-2026-11-10.txt). I also checked the
              test-first deadline fix, reviewed the disputed job advertisements myself, and
              documented the known Oscar Physician Reviewer limitation as an expected failure. The
              earlier live runs predate the deadline fix, so I am not claiming that the new deadline
              behavior was verified in a live run.
Not checked:  - A real Relevant posting: run 3 judged 6 real new postings, all Not Relevant, so the
                Relevant path inside the loop ran only in tests. I decided Palantir's "Dev"
                department should count as engineering for Palantir only (review/19), but that
                reading is not built or tested.
              - A real timeout or 5xx: retries were only exercised with constructed responses.
              - The strict time deadline against a real slow server: it is tested with a
                constructed clock only, and the live runs predate it.
              - The gap between checking a path and writing it, and hard links (not tested).
              - A real redirect: the redirect guard was tested on a constructed redirect only.
              - A partial Ashby or Lever response: the check can only catch truncation on
                Greenhouse, which reports meta.total.
              - The rule's reading of experience and remote beyond the phrasings in these 685
                postings; the Physician Reviewer office-tag case and the location-vs-offices
                question are known and open.
Not claiming: I am not claiming that every posting classification is correct, including
              Claude Code's interpretation of the changed postings, which I reviewed through
              review/17 and by reading the disputed job advertisements myself (review/19).
              Nor that the agent finds good jobs, that rule v2 is correct in general (it is
              checked against 20 per-condition hand labels), that a clean exit means a right
              answer, or that the budgets are the right size for more than these six boards.
Signed: Shreyash Yadav, 11/10/2026
```

## Driver's seat

| Part | Claude should | Shreyash should | Why that part stays Shreyash's | Where the split shows |
|---|---|---|---|---|
| The exits, budgets and policy | turn GATE.md into code and tests; mark each choice the gate leaves open | write the gate first; decide what "finished" means and what needs approval | the limits on what an agent may do are the owner's decision, not the agent's | `9fbab0d` is GATE.md alone, in Shreyash's words; the choices are in GATE-NOTES.md |
| The loop's run | run it, save the trace and raw files, recount independently | choose the boards and the deliberate failures | which boards to watch and which failures to stage is a judgment about the search | GATE.md section 1; TRACE.md |
| The review: reading the diff | produce the behavior diff over real postings; list every condition that stops failing; find causes | run the commands; read the evidence; decide accept, revise or reject | a green test run is Claude's to produce; whether the change is right is the owner's call | `review/04` and `review/17` (Shreyash's runs); `review/05` "I don't want to accept the patch just because the tests are green"; `review/18` |
| What the rule should mean | point out cases the rule cannot settle | settle them, or leave them open on purpose | it decides which jobs are worth a day | Shreyash's JS1 decisions on experience and remote; the location-vs-offices case left open in `review/18` |
| The sign-off | draft the lines | check them, change them, sign or withhold | only the signer knows what they did not test | the signature line above |
