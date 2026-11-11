# Sign-off — Job-Search Agent 2

Drafted by Claude Code from the tests and runs on 2026-11-10; read and signed by Saloni
("Signed, push it", in chat, 2026-11-10 ~20:10 ET).

```text
Sign-off — Job-Search Agent 2

Checked:      - a 404 board is not retried, reports no counts (null, not 0) and makes the run
                incomplete (test_404_not_retried_board_failed_no_counts_run_incomplete; live runs 1-4)
              - an empty board is suspicious, not "finished, 0 new", and wrong version 1 is caught
                (test_wv1_empty_board; FINISHED-WRONG.md + scripts/independent_check.py)
              - a failed or timed-out board never lets the run say finished; wrong version 2 is
                caught (test_wv2_failed_board, test_timeout_twice_fails_after_one_retry)
              - the same id on two boards is two jobs; wrong version 3 is caught
                (test_same_id_on_two_boards_is_two_jobs, test_wv3_bare_id_is_caught)
              - old-format history migrates without hiding or inventing a new job, on real data
                (test_real_run1_history_migrated_reports_only_the_real_new_job; live runs 3 and 4)
              - budgets: requests, seconds, boards; a retry counts; most serious status wins
                (TestBudgetsAndRepeats); config cannot drift from GATE.md (tests/test_gate.py)
              - repeat rule: the same method+host+path is skipped and costs no budget
                (test_same_board_twice_is_repeat_skipped_no_budget)
              - permission policy: 21 boundary cases, 21/21 pass (tests/test_policy.py,
                BOUNDARY-TESTS.md)
How:          - boundary predictions: by hand, by me, committed before the tests ran (39dea2de);
                19/21 matched, and I was wrong on B03
              - wrong version 3 and the migration: tests written before the patch they test
                (75a70e03 before 08951265; 6a453ccf before v2), and I re-ran the reproduction
                myself on the unpatched code (review/05)
              - the hidden Korea job: by recomputation. Claude Code compared run-1 and run-2 raw
                ids; I confirmed it with live run 3, which reported exactly that job
              - the loop, policy and other tests: written by Claude Code in the same session as
                the code, not before reading it; I ran the full suite myself (review/06, review/12)
Not checked:  - a real retry: no real run had a timeout or a 5xx, so retries are shown only on
                fake responses
              - pagination or partial responses: the code assumes one response holds every job
                (true on 2026-11-10: 679 / 144 / 827)
              - the same job posted on two boards under different ids (counted twice)
              - migrate() when a board's last saved attempt is a failure (no test, no real case)
              - file races (the path is checked, then opened) and case-only path tricks on
                macOS (OUT/ vs out/ is refused, not handled)
              - any second day: four live runs, all within 15 minutes on one evening
              - each company's site terms beyond the API being public for job boards
Not claiming: that the agent finds every new job (only these three boards, only while it
              runs), that a job is relevant (JS2 does not judge), or that 50 green tests mean
              correct: patch v1 passed 48/48 and still hid a real job.
Signed or withheld: Signed: Saloni Mathure, 2026-11-10
```

**B21**: I predicted deny; the code asks for approval when an alias (symlink) points at the
history file. I decided to keep needs approval: the alias cannot bypass the approval, and the
underlying write is still the protected one (BOUNDARY-TESTS.md).

GATE.md §8 (exits, "empty unexpectedly", job identity) was drafted by Claude Code. Signing
above confirms it as mine.

## Driver's seat

| Part | What Claude should do | What I should do | Why that part stays mine | Evidence |
|---|---|---|---|---|
| **Loop: rules** | offer options, show what each one costs | choose the exits, budgets, retry rule and permissions; write the wrong versions and the failure sentence | the loop is measured against my rule; if Claude writes the rule, nothing is measured (my JS1 grade) | GATE.md §6–7 (my wording; the §6 ideas came from Claude's example list), commit `5d221da6` before any code |
| **Loop: code + runs** | write the loop, policy and tests; run them; save every raw response and trace | check the trace against GATE: did the 404 make it `incomplete`, with no counts? | a stop is not a success; only I decide whether "incomplete" is acceptable for my search | TRACE.md; `out/runs/*/report.json` |
| **Boundary tests** | write the cases and the tests | predict each case before running, and own the mismatches | a prediction written after the run proves nothing; B03 shows what I actually remembered of my own policy | `39dea2de` (predictions) before `e4ec7a53` (results) |
| **Review: reproduce + test first** | write the failing test, commit it before the patch | re-run the failure myself on the unpatched code | I have to see the defect, not take Claude's word that it existed | `75a70e03`; `review/05-saloni-before-patch.txt` |
| **Review: decide** | write the patch; explain the diff as behaviour; point out what the tests don't cover | read the diff, run the live check, decide accept / revise / reject on evidence | the green suite (48/48) said accept; my live run said revise. Claude can't be the one to judge its own patch | `review/07`, `review/08-saloni-decision-v1.md`, `review/13`, `review/14` |
| **Sign-off** | draft Checked / Not checked from the tests | edit, and sign or withhold | my name goes on it | this file |
