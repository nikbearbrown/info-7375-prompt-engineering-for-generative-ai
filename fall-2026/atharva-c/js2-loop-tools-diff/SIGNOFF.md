# SIGNOFF.md

## 1. What I Checked and How

* **Policy Enforcement (Tests Before Code):** Verified all 12 boundary checks in `tests/test_policy.py` (`test_b01` through `test_b12`). These tests were defined in `BOUNDARY_TABLE.md` prior to code generation. I executed the suite locally using `python3 -m unittest` and committed the passing run log in `evidence/policy-tests-20261108.txt` (commit `6981c72`, testing policy code from `f357831`).
* **Non-Retry on 404 & No Fake Counts (Unit Tests + Manual Trace Audit):** Verified via `test_wv04` and `test_wv11` in `tests/test_loop.py`. Additionally, I audited the raw trace of the first live run (`evidence/run-20261109-041358Z/trace.jsonl`), confirming by hand that the deliberate fake board (`nonexistent-co-xyz`) executed exactly 1 attempt, dispatched zero retries, and recorded no synthetic job counts.
* **Empty Boards Flagged and Run Ends Incomplete (Unit Test + Independent Verification):** Verified via `test_wv01`. I also validated this behavior dynamically by running the finished-wrong-answer demo: when Robinhood was seeded with zero jobs, the naive loop marked the run finished, but `independent_check.py` detected the anomaly and flagged that Robinhood dropped from 153 to 0 jobs.
* **Budget Ceilings & Halting Logic (Unit Tests + Live Demo):** Verified through `test_wv12`, `test_board_budget`, `test_request_budget`, and `test_request_budget_used_up_between_boards`. I also tested this live by executing the budget-exhausted demo with a 2-request limit, confirming the loop stopped immediately after 2 requests, reported `budget-exhausted`, and recorded unqueried boards as `not reached`.
* **Skill Matcher Defect Resolution (Test-Driven Review Packet):** Verified via `tests/test_skills.py`. The suite failed with 7 failures across 6 tests in `e5a4ebc` (RED) on my test labels. After Claude's patch in `80e4fa1` (GREEN), all 6 skill tests passed, bringing the full test suite to 35/35 passing. I re-ran `reproduce_skills` against saved Wealthfront payloads to verify that the 2 false positives disappeared while the 3 genuine engineering roles remained.
* **New-Job Diff Integrity (Independent Raw Recomputation):** Verified the incremental additions between the two live runs by running an independent diff script directly comparing the raw payload files (`evidence/run-20261109-041358Z` vs. `evidence/run-20261110-025626Z`). The independently calculated counts matched the agent’s reported values exactly without relying on `out/seen.json`: Robinhood +6, Affirm +5, Wealthfront +0.

---

## 2. What I Did Not Check

1. **Real-world 5xx server errors and live network timeouts:** Tested exclusively using a fake fetcher that returned scripted responses or raised a mock timeout; no live production endpoint returned a 5xx or timed out during the actual runs.
2. **Impact of removed job postings:** The agent tracks only newly seen posting IDs and does not diff against dropped IDs. I did not evaluate the impact of unnotified deletions (e.g., the 3 postings removed from Robinhood and 6 removed from Affirm between live runs).
3. **Website Terms of Service:** I checked technical HTTP response codes on the target API hosts; I did not review the formal terms of use for Affirm, Robinhood, or Wealthfront.
4. **Validity of the 50% drop threshold in `independent_check.py`:** The 50% drop trigger was selected as a working heuristic for the demo; it has not been calibrated or stress-tested against historical job fluctuation distributions.
5. **Multi-page API responses (Pagination):** Did not test boards with posting volumes that exceed a single payload response.
6. **Cross-platform filesystem portability:** Execution and boundary paths were verified only on macOS (Darwin); no verification was run on Linux or Windows.

---

## 3. What I Am Not Claiming

* **I am not claiming this agent identifies "relevant" or "good" jobs:** The loop finds newly posted IDs; the skill extraction engine remains an isolated component and is not connected to filter the live run output.
* **I am not claiming skill matching is comprehensive:** The regex rules deliberately miss hyphenated forms like "Go-based" and all-caps headings like "REACT" to protect against broader conversational false positives.
* **I am not claiming the budget numbers are globally optimal:** The limits (5 boards, 15 requests, 60 seconds) represent an intentional developmental bound to catch runaway loops, not an optimized balance for enterprise scraping.

---

## 4. Why the System Stays Mine (Driver's Seat)

| Component | Decision I Made | Evidence | Why It Matters / Why It Stays Mine |
|---|---|---|---|
| **Loop Architecture** | Flagging empty 200 OK boards as `empty-response` and ending the run `incomplete` rather than reporting "no new jobs." | `GATE.md` (`777cef4`), `WRONG_VERSIONS.md` (#1) | A clean `finished` exit would silently hide broken boards, mistyped slugs, or upstream schema deprecations. Claude's naive version demonstrated how easily an uninspected empty payload masks a failure. |
| **Budget Policy** | Setting hard ceilings at 5 boards, 15 requests, and 60 seconds, with an operator-only change rule. | `GATE.md` (`777cef4`), `budget.json` | Left unconstrained, automated retry loops burn requests on dead endpoints. I reserved a 1-retry cap per board and made modifications require a committed edit to `GATE.md`, keeping operational authority with the human operator. |
| **Repeat Handling** | URL normalization (stripping trailing slashes, lowercasing path) and charging zero budget for skipped duplicates. | `GATE.md` (`777cef4`), `WRONG_VERSIONS.md` (#2, #3) | Prevents redundant network calls when slugs vary only by case or trailing slashes, ensuring budget is consumed exclusively by dispatched I/O. |
| **Review Packet** | Categorizing the 5 Wealthfront postings, reversing my initial labels on "react to insights" and "go-to designer", and accepting the patch trade-offs. | `e5a4ebc`, `REVIEW_PACKET.md` | Deciding whether a term represents an engineering competency or conversational prose requires domain judgment about job requirements, not automated regex matching. I chose to accept misses on "Go-based" and "REACT" to keep the rule boundaries tight. |
| **Permission Exception** | Establishing the `--approve` flag requirement to allow protected configuration writes outside `out/`. | `GATE.md` (`777cef4`), `tests/test_policy.py` (`test_b09`, `test_b10`) | Balancing strict filesystem isolation (`out/` only) against necessary configuration updates (`boards.json`, budget caps) requires an explicit, auditable operator override rather than an open write permission. |

---

## 5. Sign-off

* **Status:** Signed
* **Operator:** Atharva C.
* **Date:** November 9, 2026
