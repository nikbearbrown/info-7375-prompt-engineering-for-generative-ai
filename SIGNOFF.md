# Sign-off: Job-Search Agent 2

> *Drafted by Claude Code on 2026-11-10 from the commits and outputs in this folder. Ethan: read it, put it in your own words, run the
> commands, then sign. Delete this note when you do.*

**Checked:** which properties, by which of my own tests

| Property | Test(s) or evidence |
|---|---|
| Path escapes refused: `..`, `out-evil/`, symlinks, `--out config/` | `test_W1_prefix_trick_out_evil`, `test_W2_symlink_escape`, `test_W16_*`; boundary B08–B10, B16 |
| Read vs write: config readable, not writable; nothing outside the listed folders read | `test_W11_write_config_denied`; B11, B12, B17 |
| Existing evidence never overwritten without a named approval | `test_W12_overwrite_needs_approval`, `test_reset_state_needs_approval`; B14, B15 |
| Hosts: exact match, lookalikes refused, HTTPS GET only, port 443, no user information | `test_W3_lookalike_host`, `test_W4_*`; B01–B06, B18 |
| Every redirect hop checked and charged to the budget | `test_W5_redirect_hops_count`; B07 |
| A failed board is null, never 0, and makes the run incomplete | `test_W6_failed_board_count_null`, `test_W7_failed_board_incomplete`; live run A (`samsara-does-not-exist`) |
| Retries counted; a 404 never retried; 500 once; 429 only with a short Retry-After | `test_W8_*`, `test_W9_no_retry_on_404`, `test_http_500_retried_once_429_with_long_wait_not_retried`; run A trace (1 attempt) |
| Repeat rule normalizes URLs | `test_W10_trailing_slash_is_repeat`, `test_duplicate_boards_removed_before_loop` |
| State: failed boards untouched; unjudged postings stay new | `test_W13_failed_board_state_unchanged`, `test_W14_unjudged_stay_new` |
| The verifier is independent and fails empty boards | `test_W15_verifier_ignores_report_counts`, `test_W19_empty_board_fails_verification`; runs B and C |
| Config matches the gate | `test_W17_allowlist_matches_gate`, `test_W18_budgets_match_gate` |
| Each wrong version is actually caught | `scripts/sabotage_check.py`: 19/19 RED (`evidence/tests/04_sabotage_check.txt`) |
| Samsara compared with the real Oct 31 baseline | run A: 80 new. I recounted by hand from the raw file, and none is data-titled |

**How:**
- **By a test written before reading Claude's code:** the W1–W19 tests and the B01–B18 predictions were committed in `e51d208`, before
  any JS2 code. *Claude wrote those tests too, from GATE.md. What makes them "before" is the commit order, not who typed them.*
- **By recomputation:** the verifier recounts from raw bytes. I checked by hand that none of Samsara's 80 new titles matches
  `data|analytic`. Kraken's 92 Ashby postings came from my cross-check outside the agent.
- **With Claude's help:**
  - all the code
  - the GATE.md drafts (my own edit is `a67bdbf`)
  - the boards probe
  - the patch (`afb3877`)
  - these documents
- **By hand:** *Ethan: list what you reran yourself, with dates (REVIEW_PACKET.md section 5).*

**Not checked:**
1. **Live retries, redirects and 429s.** None happened in runs A–D. Those paths are tested only against a scripted fetcher.
2. **The rule judge on a live posting.** No new data-titled posting appeared in any live run. Judging is covered only by offline tests.
3. **A proxy set in the environment** (`HTTPS_PROXY`). `urllib` would route through a host that isn't on the allow-list. See the review
   packet.
4. **A race between the path check and the write** (a symlink swapped in between), and hard links.
5. **A real second day for boards 2–9.** B and D ran 27 s and 71 s after A.
6. **Each site's full terms of use.** I relied on these being public job-board APIs and kept to about 30 paced requests.
7. **The Claude-judge path inside the JS2 loop** (`--no-claude` was used every time).
8. The verifier trusts earlier reports' lists of unjudged ids.

**Not claiming:**
- that the agent finds every relevant job
- that any verdict is right for a real person
- that Kraken or any other company has (or lacks) a fitting role
- that the agent works on any system other than Greenhouse and Lever
- that the same-day runs show change over time

**Signed or withheld:** ____________ *(Ethan Gomes, date)*. Withheld until I have rerun the commands above myself.

---

## Driver's seat

| Part | What Claude did | What I did | Why it stays mine | Evidence |
|---|---|---|---|---|
| **The loop's rules** (exits, budgets, repeat, errors) | Drafted GATE.md v1–v2.3 from my outline; proposed numbers and gaps | Chose the format, asked for ten boards, turned the judge off, kept Kraken over Airbnb, made my own edit, approved v2.3 before code | What counts as "done" and "too much" is my decision; a model can't raise its own budget | `82f02cb`…`6cc9e07`; my edit `a67bdbf`; GATE.md Decisions log |
| **Boards** | Probed Greenhouse, Lever and Ashby read-only; found Kraken's `200 []` and its 92 Ashby postings | Picked Lever over Ashby and Kraken over Airbnb | Which companies I watch is a personal call | GATE.md Scope; `evidence/crosscheck/` |
| **The loop's code** | Wrote `policy.py`, `providers.py`, `net.py`, `loop.py`, `verify_run.py` and the tests | *Ethan: what you read and reran* | I am responsible for what the agent may touch, so I have to understand the policy code, not just see green tests | `e51d208` (tests first), `6c82b59` |
| **The review** | Reproduced the defect, wrote the 9-line patch, ran the before/after commands | *Ethan: reran the commands, decided accept, revise or reject* | Accepting a diff is a judgment about behavior I'll live with; "tests pass" isn't that judgment | `58ce031`, `afb3877`, REVIEW_PACKET.md |
| **The finished-wrong answer** | Built the verifier and the seeded run | *Ethan: confirmed the Kraken cross-check means the answer is wrong* | Deciding an answer is wrong needs evidence from outside the agent | FINISHED_WRONG_ANSWER.md, RUNS.md |
