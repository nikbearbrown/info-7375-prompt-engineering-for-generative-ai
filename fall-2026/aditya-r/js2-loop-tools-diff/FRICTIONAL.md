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

## [process log] 18:36–19:55 — Aditya's approval and check; the attempt-deadline fix

- Aditya ran the approval demonstration (18:36–18:38) and the fresh-extraction check (18:41–18:42) himself. His outputs were committed byte-identical (`e1a4a69`), except for one pip temp-folder path, which was redacted and disclosed.
- He asked for the documented DNS gap to be resolved without weakening the gate.
- **Friction:** writing the tests showed the gap was wider than the README said. The TLS handshake, status line and headers each got a fresh socket timeout on every `recv`, so a dripping server held an attempt for 3.02 s against a 0.5 s deadline. An expired deadline also still connected.
  - The tests were committed failing (`20c9d05`: 4 failed, 3 passed).
  - The fix is `be5d821`.
- **Friction:** the fix broke B7. The cause was a fake test clock fed to the real client, not the redirect logic. Only B7's wrapper changed; its assertions did not.
- **Friction:** the first mutation run with the new mutants had 1 MISSED. A negative connect timeout raised `ValueError` and masked the removed check. The mutant was strengthened, and the run is kept (`evidence/mutation/mutation_check_js2_dns_first_run.txt`). Result: 21/21.
- The LIVE run and the approval demonstration were **not** rerun. They ran on the earlier client, and their records are unchanged.

## [Aditya] Entries — written by Aditya

_Provenance: written by Aditya and dated by him November 10, 2026. He gave the text to Claude Code in the session, and Claude inserted it below verbatim at 2026-11-10 19:42 EST. Claude changed only the Markdown heading levels; it edited none of the words._

Date: November 10, 2026

### 1. Reproducing a successful-looking wrong result

I ran Claude’s P2 probe against the inherited implementation. Its synthetic response contained one posting but declared `meta.total = 40`. The agent nevertheless reported `COMPLETE` and returned exit 0.

The same posting was already in the baseline, so finding zero new IDs among the supplied records was understandable. The problem was accepting inconsistent acquisition evidence and presenting the run as complete.

I then ran the AI-authored regression test. It failed at the behavioral assertion `assert 0 == 3`, with pytest exit status 1. This gave the patch a concrete before-and-after check.

The state-preservation assertion came after the failing exit-code assertion. Therefore, that first failing run did not establish whether state was preserved. I needed the later passing run to exercise that assertion.

Evidence: `review/investigation_output_P2.txt`, `review/prepatch_failure.txt`, and `tests/test_aditya_total_mismatch.py`.

### 2. Requesting a revision after the first patch passed

The first patch passed my regression, the 93-test suite, and the three inherited mutation checks. During the review, i identified that a present non-object `meta` value still bypassed validation.

I supplied a REVISE decision: absent optional metadata should remain permitted, but present malformed metadata should be rejected. This distinction was an explicit clarification to the original request, not a defect I independently discovered.

After Claude implemented the revision, I ran the checks again. The targeted tests reported 21 passed, the full suite reported 113 passed, and the inherited mutations were caught. I then accepted the scoped patch.

Passing the first test suite did not cover every interpretation of the request. The review added a specific missing case while keeping the patch focused.

Evidence: `review/aditya_postpatch_run.txt`, `review/aditya_final_check.txt`, and the reproduction, patch, revision, and acceptance chronology in `review/REVIEW.md`.

### 3. Keeping incomplete work visible

The recorded live run ended `budget-exhausted`, exit 4. It used the ten permitted judgment calls and left 79 postings pending. The deliberate 404 board remained a failed board with unknown counts represented as `null`.

I accepted this outcome under the written budget and exit-precedence rules. I did not request a higher budget or replacement judgments merely to make the report appear complete.

This also limited the shortlist. Four RECORD-relevant postings lacked validated judgments and were withheld, leaving an empty export explicitly marked partial. That export does not establish that no suitable jobs existed.

Evidence: the saved live report and trace under `out/runs/20261110T232115022Z_live/`, and the export proposal.

### 4. Exercising the approval boundary myself

I inspected the proposal and export contents and ran the export without approval. It returned exit 3.

I then executed the approval-record creation command myself. The helper, checked the proposal and content hash and recorded the actual approval time. I authorized only the exact proposed local file.

The approved export returned exit 0, and the byte comparison confirmed that the created file matched the proposal. A repeated export returned exit 2 because the destination already existed.

This demonstrated the intended distinction between having permission to propose a write and having permission to perform that exact write. The approval did not authorize applications or messages, and it did not change the original live run’s status.

Evidence: `evidence/approval_demo.txt`, the approval record, and the approved export.

### 5. Checking reproducibility and recording remaining limits

I ran `scripts/clean_clone_check.sh` myself. It extracted committed revision `1019351`, created a fresh environment, and ran the verification commands. The result was 171 passing tests, all declared mutations caught, 24 evidence checks with no contradiction found, and exit 0.

The mutation output contained `FAILED` lines identifying tests that detected deliberately broken implementations. Those lines were accompanied by `CAUGHT` results; they were not failures of the unchanged implementation.

The fresh extraction is stronger evidence of reproducibility than relying only on my existing working environment. It is not a fresh live collection, and it does not independently prove the correctness of every test or checker.

I have not personally validated the 79 pending judgments, established behavior across multiple live days, or proved that count agreement implies accurate posting contents. The documented DNS deadline gap also remains unresolved at this checkpoint. Later fixes will require their own evidence.

My next steps are to review those final changes, run the final verification against the resulting revision, and decide what I can accurately include in my sign-off.
