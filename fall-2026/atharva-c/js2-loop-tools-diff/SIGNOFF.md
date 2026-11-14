# SIGNOFF.md

## 1. What I Checked and How

* **Policy Enforcement (Tests Before Code):** Verified all 12 boundary checks in `tests/test_policy.py` (`test_b01` through `test_b12`). These tests were defined in `BOUNDARY_TABLE.md` prior to code generation. I executed the suite locally using `python3 -m unittest` and committed the passing run log in `evidence/policy-tests-20261108.txt` (commit `6981c72`, testing policy code from `f357831`).
* **Non-Retry on 404 & No Fake Counts (Unit Tests + Manual Trace Audit):** Verified via `test_wv04` and `test_wv11` in `tests/test_loop.py`. Additionally, I audited the raw trace of the first live run (`evidence/run-20261109-041358Z/trace.jsonl`), confirming by hand that the deliberate fake board (`nonexistent-co-xyz`) executed exactly 1 attempt, dispatched zero retries, and recorded no synthetic job counts.
* **Empty Boards Flagged and Run Ends Incomplete (Unit Test + Independent Verification):** Verified via `test_wv01`. I also validated this behavior dynamically by running the finished-wrong-answer demo: when Robinhood was seeded with zero jobs, the naive loop marked the run finished, but `independent_check.py` detected the anomaly and flagged that Robinhood dropped from 153 to 0 jobs.
* **Budget Ceilings & Halting Logic (Unit Tests + Live Demo):** Verified through `test_wv12`, `test_board_budget`, `test_request_budget`, and `test_request_budget_used_up_between_boards`. I also tested this live by executing the budget-exhausted demo with a 2-request limit, confirming the loop stopped immediately after 2 requests, reported `budget-exhausted`, and recorded unqueried boards as `not reached`.
* **Skill Matcher Defect Resolution (Test-Driven Review Packet):** Verified via `tests/test_skills.py`. The suite failed with 7 failures across 6 tests in `e5a4ebc` (RED) on my test labels. After Claude's patch in `80e4fa1` (GREEN), all 6 skill tests passed, bringing the full test suite to 35/35 passing. I re-ran `reproduce_skills` against saved Wealthfront payloads to verify that the 2 false positives disappeared while the 3 genuine engineering roles remained.
* **New-Job Diff Integrity (Independent Raw Recomputation):** Verified the incremental additions between the two live runs by running an independent diff script directly comparing the raw payload files (`evidence/run-20261109-041358Z` vs. `evidence/run-20261110-025626Z`). The independently calculated counts matched the agent’s reported values exactly without relying on `out/seen.json`: Robinhood +6, Affirm +5, Wealthfront +0.

### Verification Methods ("How")
Every item above was verified using one of four specific methods:
* **By hand:** Auditing the raw `trace.jsonl` log from live run 1 to verify the 404 response on `nonexistent-co-xyz` executed exactly 1 attempt with no retries and no invented count; reviewing the raw diff of the patch in `review/02-patch-20261109.diff`.
* **By a test I wrote before reading Claude's code:** Specifying all 12 boundary test cases and predicting their exact outcomes in `BOUNDARY_TABLE.md` (`75ff81e`) before any policy code existed; documenting all 12 failure modes and their catching tests in `WRONG_VERSIONS.md` (`459e7b3`) before test implementations were drafted; and manually labeling the positive and negative test cases for React and Go before the patch was written.
* **By recomputation:** Recomputing the new-job counts independently by running the diff script directly against the raw payload files of the two live runs (`evidence/run-20261109-041358Z` vs `evidence/run-20261110-025626Z`), matching the agent's reported additions (Robinhood +6, Affirm +5, Wealthfront +0) without reading `out/seen.json`.
* **With Claude's help:** Claude wrote the Python implementation code for the tests (`test_policy.py`, `test_loop.py`, `test_skills.py`), the loop and policy logic, the recomputation script (`independent_check.py`), the naive demo scripts, and the bug fixes. My verification was limited to running those test suites locally, reading the emitted logs/traces, and confirming the failure modes matched my upfront specifications.

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

| Component | What Claude Should Do | What I Should Do | Decision I Made & Evidence | Why That Part Stays Mine |
|---|---|---|---|---|
| **The Loop** | Write the loop runner and test code; flag gaps in coverage or reporting. | Set exits, budgets, and error policy before code; read the trace; run the tests. | Decided empty 200 OK boards are flagged as `empty-response` and end `incomplete` rather than reporting "no new jobs". Evidence: `GATE.md` (`777cef4`), `WRONG_VERSIONS.md` (#1). | A clean `finished` exit would silently hide broken boards or upstream schema changes. Only the operator can decide what level of data integrity constitutes a real success. |
| **Budgets & Permissions** | Draft the policy functions (`policy.py`), budget counters, and boundary tests based on table inputs. | Set hard budget ceilings, establish change-authority rules, and approve file write exceptions. | Established the 5 boards / 15 requests / 60s limits, restricted modifications to committed `GATE.md` edits by me, and required `--approve` for protected writes. Evidence: `GATE.md` (`777cef4`), `tests/test_policy.py` (`test_b09`, `test_b10`). | Preventing runaway scraping costs and unintended filesystem modifications requires non-delegable operator authority. An automated agent cannot self-authorize budget increases. |
| **The Review Packet** | Propose the patch diff (`skills.py`); flag side effects, edge cases, and docstring mismatches. | Label the cases; write the prompt; read the diff; decide the final verdict. | Labeled the 5 Wealthfront postings, corrected initial false assumptions on "react to insights" and "go-to designer", and accepted trade-offs on "Go-based" and "REACT". Evidence: `e5a4ebc`, `REVIEW_PACKET.md`. | Determining whether a keyword represents a technical qualification or casual conversational prose is a domain judgment about hiring, not a code generation task. |
| **Repeat Handling** | Implement URL parsing, dictionary tracking, and test harnesses for duplicates. | Define what makes two requests identical and whether duplicate evaluations consume budget. | Required URL normalization (stripping trailing slashes, lowercasing path) and charged zero budget for skipped duplicates. Evidence: `GATE.md` (`777cef4`), `WRONG_VERSIONS.md` (#2, #3). | Prevents redundant network calls when slugs vary only by casing or trailing slashes, ensuring budget is consumed exclusively by dispatched I/O. |

---

## 5. Sign-off

* **Status:** Signed
* **Operator:** Atharva C.
* **Date:** November 9, 2026
