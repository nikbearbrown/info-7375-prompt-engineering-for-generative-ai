# Sign-off: Job-Search Agent 2

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
- **By hand:** on 2026-11-10 at 17:31 EST I reran these in my own terminal, and every result matched what was expected (results in
  REVIEW_PACKET.md section 5):
  - `git show afb3877 -- jsagent/fetch.py` and `git show --stat afb3877`: I read the patch and checked its scope myself
  - `review/reproduce_port_userinfo.py`
  - the full test suite (113 OK)
  - `scripts/sabotage_check.py` (19/19 caught)
  - `scripts/boundary_report.py` (18/18)
  - `scripts/verify_run.py` on runs A, B and D
  - a `grep` of run A's trace for the deliberate 404

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

**Signed or withheld:** Signed, Ethan Gomes, 10 November 2026

---

## Driver's seat

For each part: what Claude should do, what I should do, why my part stays mine, and the evidence of what actually happened.

### The loop

| Part | What Claude should do | What I should do | Why that part stays mine | Evidence (what actually happened) |
|---|---|---|---|---|
| **Exits and budgets** | Draft the gate's wording; find gaps and contradictions; propose numbers with the arithmetic behind them | Decide what "finished" means, the board/request/time ceilings, and who may change them; approve the gate before any code | A budget is a limit on what I let the agent spend. A model can't raise its own ceiling, and "stopped" vs "succeeded" is my definition | GATE.md v1→v2.3 (`82f02cb`…`6cc9e07`), all before code (`e51d208`). Budgets raised only with a Decisions-log row (v2.2). My own edit: `a67bdbf` |
| **Boards and systems** | Probe read-only and report what came back, including surprises | Choose which companies and which systems the agent watches | Which jobs are worth watching is a personal call | I asked "can you include 10 boards in total?" and "Do what you think is best in adding Kraken or changing to Airbnb". The probe found Kraken's `200 []` and 92 postings on Ashby (GATE.md Scope, `evidence/crosscheck/`) |
| **Permission policy** | Write the policy code and the boundary cases from the gate, with predictions committed before the code | Decide the hosts, the folders, what needs my approval, and what is never allowed; read the policy code | I'm responsible for what the agent can touch. Green tests aren't the same as knowing what is allowed | Predictions B01–B18 in `e51d208` before `jsagent/policy.py` existed. I reran `scripts/boundary_report.py` on 2026-11-10 17:31: 18/18 |
| **Loop code and tests** | Write tests first, then the code; run them and report failures honestly, including its own mistakes | Rerun the tests and the sabotage check myself; check that a test means what the gate says | A passing suite only means something if I know what it tests | 59 red before code (`evidence/tests/01_…`), 5 red after the build (`02_…`). My reruns on 2026-11-10 17:31: 113 OK, sabotage 19/19 |
| **Judging an answer wrong** | Build an independent verifier that does not import the loop, plus a labeled seeded replay | Decide, from evidence outside the agent, whether a "finished" answer is wrong | The agent can't grade itself. The Kraken call needed a source the agent isn't allowed to reach | Run B finished with kraken at 0 new; the Ashby cross-check found 92 postings. My reruns of the verifier on runs A/B/D: FAIL/FAIL/PASS |

### The review

| Part | What Claude should do | What I should do | Why that part stays mine | Evidence (what actually happened) |
|---|---|---|---|---|
| **Reproduce and test first** | Reproduce the defect before touching code; commit the failing test first | Check that the reproduction and the failing test exist before the patch, in the commit order | "Test first" is only proof if the history shows it | `58ce031` (reproduction, no code change) comes before `afb3877` (patch). The W4 tests date from `e51d208` |
| **The patch** | Make the smallest change that meets the gate; show before/after; name what the test still misses | Read the diff myself as a change in behavior, and check its scope | I live with what the code does, not with Claude's summary of it | I ran `git show afb3877 -- jsagent/fetch.py` and `git show --stat afb3877`: +9 lines in `check_url`, code scope 1 file (REVIEW_PACKET.md section 5) |
| **The decision** | Lay out the evidence. It should **not** decide | Rerun the commands and decide accept, revise or reject | Accepting a diff is my judgment, and "tests pass" isn't that judgment | My reruns 2026-11-10 17:31 all matched. Decision: see REVIEW_PACKET.md section 6 |
