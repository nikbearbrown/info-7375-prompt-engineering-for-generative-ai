# FRICTIONAL — Job-Search Agent 2

- **[process log]** entries record what happened in the Claude Code session. Claude Code drafted them from commits and saved outputs; times are EST on 2026-11-10.
- **[Aditya]** entries are Aditya's own account. Claude did not write them.

## [process log] Before the gate (session start not recorded; recon file 13:31:46 EST) — Requirements, JS1 provenance, recon

- Read both PDFs, the four policy pages, and the JS1 code, tests and docs.
- **Found:** JS1's local repo (`819f2e9`, 20 commits) was never pushed as history. The course repo has one squashed commit, `693b7d3`. The ZIP, the local HEAD and the posted folder share tree `4ccb1e5`.
- **Pre-gate recon:** at 18:31:46Z, status and shape only. Ashby ids are string UUIDs, which JS1's integer-id parser rejects. Invalid boards return 404 on both providers, not an empty 200. That is why the empty-board case had to be REPLAY or SYNTHETIC.
- Sealed eight observations about the baseline (sha256 `b9206df8…`, kept local) so that later attribution could be checked.

## [process log] 16:16–16:35 — Gate committed first; baseline; first push

- Aditya's GATE.md was committed byte-identical (`8257ffb`) before any code.
- The baseline was imported, and the inherited checks passed: 72 tests, 3/3 mutants, verify_evidence.
- **Friction:** before the first push, a scan found Aditya's absolute local path in `baseline_checks.txt`. My `sed` had sanitized only the "started in" lines. Aditya chose to rewrite the three unpushed commits. The mapping is recorded in `BASELINE.md`; only `8257ffb` had been pushed.
- Aditya's six clarifications were saved verbatim (`8a0ef83`).

## [process log] 17:20–18:11 — Review cycle (Aditya's reproduction, test, decision)

- Aditya's five files were committed before any fix (`b0e3fb4`). One username redaction was disclosed.
- The patch is `0007bbd`. Aditya's round-1 check passed, and he still decided **REVISE**. He rejected Claude's interpretation that a non-object `meta` means "no total".
- The revision tests were committed failing (18 failed, 2 passed; `41c342d`) before the revision (`d58682c`).
- Aditya accepted after his 18:03 check (`9589e64`). He noted that the inherited mutants did not cover the new validation. That note led to the W1 meta mutants in `mutation_check_js2.py`, which are now caught.
- **Push friction:** another student pushed meanwhile. I merged rather than rebased, to keep the cited hashes.

## [process log] 18:11–18:25 — Build, mutation gaps, LIVE run, demonstrations

- Boundary predictions were committed (`19f3140`) before `policy.py` and the boundary tests (`785138a`).
- **Bugs found by the tests while building:**
  - Run ids collided within one second. Fixed with milliseconds, and a collision now exits 2 instead of crashing.
  - A retry blocked by the HTTP budget was labeled as blocked by time. Fixed so that `_retry_wait` returns the budget that blocked it.
- **First mutation run: 3 MISSED.**
  - W3-http: the first-attempt budget check was never exercised with 4 boards. A new test covers it.
  - W6 and W11: each was masked by a second defense (the re-check after creating folders; out-only confinement). The mutants now remove both layers, or grant their own approval.
  - The second run caught 18/18 (`e1109cf`).
- **LIVE run** (18:21): budget-exhausted, exit 4, exactly as Addendum §6 predicted for a backlog larger than 10. The independent checker passed 24/24.
- **Finished-wrong demo** (18:24): all 4 predictions committed in `8664385` held.

## [Aditya] Entries — written by Aditya

_(Aditya: dated entries in your own words. The prompts that fit: what I tried and expected; what happened; what I did; what Claude contributed and what I accepted, changed or rejected; what I understand now and what I still don't; evidence and next step. Candidate episodes from the record, for your account only: writing the gate; choosing P2 and writing the test; the REVISE decision on non-object `meta`; the approval action.)_
