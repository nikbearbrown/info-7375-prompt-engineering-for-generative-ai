# Sign-off — Job-Search Agent 2

## Checked (property → my tests)
- Network allow-list is exact host + method + path: boundary rows 1–9, 20–26, 42;
  mutants wv01 (includes, endsWith), wv04, wv05, wv13 killed (evidence/mutants-pre-patch.txt).
- Writes stay inside out/: rows 10–16; replay reads stay inside out/raw/: rows 38–41;
  the symlinked-out/ test.
- Approvals are single-use and path-bound: rows 17–18, 27–30, 37; mutants wv18 killed.
- Budgets are checked before acting and can't be raised: rows 31–36, WV8 (both), WV15,
  WV19, the wall-clock test.
- Error policy: row 43 and WV7 (no 404 retry, one 5xx retry), the 503-then-200 test,
  rows 34–35 (Retry-After), the two injected-clock timeout tests. Live: a real timeout
  then 200 in 215021538Z.
- Exits: test 29 (incomplete, exit 10), WV9, rows 31–32; live runs ended 10, 11 and 12.
- Repeat rule: WV11. Append-only state: WV17; live, Stripe 776 jobs / 777 ids.
- ID handling: state-regression cases 1–5 failed first (`17c9225a`) and passed after the `src/state.mjs` patch (`c04d1ecf`). The duplicate-raw-ID provider/loop regression tests failed before `42c9bc52` and passed after it: a repeated ID is now a board-level `error: malformed` with no state write. Final test record: `evidence/node-test-final.txt` (123/123).
- Checker: rules 1–3 tests, the no-observations test, the Greenhouse-0 test; pre-fix
  rule 3 FAIL (evidence/check-pre-fix.txt) vs post-patch PASS (evidence/check-post-patch.txt).
- Judge disabled: row 33, WV12.

## How
- Predictions by me before any code (359ee568); test code by Claude Code against my table,
  tied to it by the meta-test (test 94).
- Regression test: cases and the STATE_INTEGRITY API specified by me before the patch;
  code by Claude Code; committed failing by me.
- Checker: recomputation from raw bytes and snapshots, never the loop's report.
- By hand: every live run, the mutant check, node --test, and the checker runs in evidence/.

## Not checked
- **Per-board null raw-ID handling remains unimplemented.** A null raw ID reaches `saveState` and ends the **entire run** as `error` (exit 12), instead of making only that board `error: malformed`/`incomplete` (interim `377fd51c`). This exception has not been resolved. **Duplicate raw IDs are no longer part of this gap**: providers reject them per board since `42c9bc52`.
- The checker rejects the legacy numeric pre-state on the migration run
  (224942910Z-post-patch-integrity): it doesn't know about the migration Decision.
- State is loaded after the fetch, so a corrupt state file still costs a request; on an
  error run, unattempted boards aren't listed and failures.json isn't written.
- UUID case variants, and loadState trusting the file's own board field.
- JS1's src/fetch.mjs reaches the network through a default parameter the fetch-grep
  test can't see; WV12 shows it is unreachable from the loop, but that is not grep-proven.
- wv03's loop-level kills are incidental (macOS /private paths), not targeted.
- Past-date Retry-After and dangling symlinks have no tests.

## Not claiming
- Any relevance judgment: the JS1 judge is disabled in JS2.
- That checker PASS means the run succeeded; it means the claims match the raw data.
- Concurrency safety (single process, no locking), or detection of postings whose
  content changes under the same id.
- That the board APIs or their terms stay as they were on 2026-11-10.
- The agent never applies, emails, messages, or logs in, and nothing here shows otherwise.

## Signed
Aravind Ravi, 2026-11-10

## Driver's seat

| Part | Claude did | I did | Why it stays mine | Evidence |
|---|---|---|---|---|
| Loop | Implemented the loop, providers, policy, trace and checker against GATE.md; found the Lever UUID bug and the GET-only need | Wrote the exits, budgets, error policy and permission rules; chose the boards; ran every live run; made every descope a dated Decision | The stopping conditions define what "done" means; an agent that sets its own exits grades itself | 359ee568; Claude Code stopped at Step 0 rather than build on the draft gate; GATE.md Decisions |
| Review | Wrote the patch, the regression test code and the behavior explanation | Reproduced the defect from snapshots; specified the 5 cases and the error API; read the diff; ran the commands; chose revise over editing tests | Acceptance needs evidence independent of whoever wrote the change | 17c9225a (failing), first patch broke JS1 tests 20/25, c04d1ecf, evidence/ |
