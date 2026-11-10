# FRICTIONAL — Job-Search Agent 2: The Loop, the Tools, and the Diff

Dated entries, written as the work happened. Times are local (America/New_York).

Each entry says what I tried, what happened, what I accepted, changed, or rejected from Claude, and the commit, prompt, or test it traces to. This log summarizes my Claude Code sessions. It does not paste transcripts: those stay on my machine, as the brief's privacy rules require.

## 2026-11-01 — Read the brief, started this log
- Pasted the JS2 brief into Claude Code and asked for its reading of the assignment, and for new files that continue from Job-Search Agent 1.
- **Where JS1 ended.** It was submitted on 2026-10-31 as branch `atharva-h/js1-contract-and-watch`, commit `f0b7a6b`, in `fall-2026/atharva-h/js1-contract-and-watch/`. It watches one Greenhouse board (Abacus Insights) with a rule judge and a Claude judge. Python standard library only; 43 tests.
- Claude created this folder, `js2-loop-tools-diff/`, with this log and an empty `GATE.md` that has only the six section headings the brief asks for.
- Nothing is built yet: no gate content, no code, no runs.
- Due Tuesday 2026-11-10, 11:59 pm ET.
- **Still to decide:**
  - what to start from: my JS1 code, the Reallocation Engine's ATS providers, or the instructor's Lectern collector
  - which boards (at least 3, on at least 2 applicant-tracking systems)
  - which board fails on purpose

## 2026-11-01 — Gate interview
- I chose to be interviewed for `GATE.md`. Claude asked one section at a time and offered options; the decisions are mine.
- **Probes before the gate.** Claude probed the three systems first. These were not agent runs, and nothing from them was saved.
  - Abacus (Greenhouse) had 18 postings, Valon (Ashby) 27, Weave (Ashby) 29, and Xsolla (Lever) 189, which took about 2.7 s.
  - A misspelled name gets a real 404 on all three systems. Ashby's 404 body is plain text, not JSON.
  - The Greenhouse slug `abacus` belongs to a different employer, "ABACUS", with 45 postings.
- **Start point:** my JS1 code.
- **Boards:** Abacus (Greenhouse), Valon (Ashby), and Xsolla (Lever).
- **Failing on purpose:** Ashby `valonn`, a real 404.
- **Finished wrong answer:** the wrong-board run, Greenhouse `abacus` posing as Abacus Insights. It is caught by a separate name check that doesn't read the loop's report.
- **Exits:** I first picked "finished, with failures listed." Claude pointed out that the gate still had to say when `incomplete` happens. I switched: `finished` only when every board succeeds, and any failed board makes the run `incomplete`.
- **Budgets and repeats:**
  - At most 5 boards, 10 requests, and 60 s per run, changed only by a dated GATE.md entry.
  - A repeat is the same method plus URL; it is refused, logged, and the run goes on.
  - A permission violation stops the run with `error`.
- **Error policy:** a 404 is never retried; a timeout or 5xx is retried once after 2 s; nothing is invented.
- **Permission policy:**
  - HTTPS GET only to the three ATS hosts, with no cookies and no auth.
  - Reads only inside this folder; writes only in `runs/` and `state/`.
  - My approval (y/N in the terminal, "no" without one) is needed to reset state, delete a run, change the board list, or write over 5 MB.
- **Wrong versions:** four, each the plausible mistake for one of my decisions: a prefix path check, a failed board read as "no new jobs", a substring host check, and retries not counted against the budget.

## 2026-11-09 — Gate additions, gate committed before code
- **Three additions to `GATE.md`, all dated, still before any code:**
  - **No judging in JS2.** The loop reports new and closed postings. JS1's judges stay in JS1. In JS1 my rule never produced `relevant` on a real posting, and JS2 doesn't need verdicts.
  - **Closed postings** are part of the `finished` report. It's the same id comparison, so it costs no extra requests.
  - **No overwrite.** A run never overwrites an earlier run's folder or report, and a normal run only adds seen ids.
- **A pre-submit check** will fail if a TODO is still open or the README claims a run with no saved trace. It's a submission tool, not part of the gate.
- **Gate committed first.** `GATE.md` and this log were committed on branch `js2-loop-tools-diff` before any JS2 code existed.

## 2026-11-09 — Build, day 1 live, finished wrong answer
- **Commit order:** the gate (`1f00955`), then the boundary-case predictions (`159adc2`), then the code (`350a997`).
- **Predictions.** `PERMISSIONS.md` lists 23 cases with their predicted outcomes and was committed before any test or policy code existed.
- **What Claude wrote,** starting from my JS1 code: `policy.py` (the gate's permission policy in code), `tools.py` (GET, read, write, new run folder, delete, each checked by the policy), `adapters.py` (Greenhouse, Ashby, Lever), `loop.py`, `agent.py`, `check_identity.py`, and `precheck.py`.
- **Bugs Claude caught in its own code before anything ran:**
  - The first `loop.py` state-update block had dead code and a helper that read a key nothing set, so it would have crashed on the first successful board.
  - Network tests needed to script responses without skipping the policy. `http_get` now always runs the policy check before handing the request to a separate send step, and tests replace only that send step.
- **Tests: 54, all passing on the first run.**
  - All 23 boundary cases came out as predicted.
  - All four wrong versions are run as mutants, and each test checks both that the mutant really gives the wrong result and that the real code doesn't.
- **Day 1, live** (`runs/2026-11-09T205756Z`).
  - Exit `incomplete`: 4 requests in 1.7 s.
  - Baselines: Abacus 15 postings, Valon 31, Xsolla 185.
  - `valonn` got a real 404 with the 9-byte plain-text body `Not Found`. It wasn't retried, its body was saved, and its state wasn't invented.
- **Finished wrong answer** (`runs/2026-11-09T205807Z_WRONG-BOARD-demo`).
  - The loop, pointed at Greenhouse `abacus` as Abacus Insights, exited `finished` (code 0) with 46 postings from a different employer.
  - The independent check (`runs/2026-11-09T205808Z_identity-check`) asked Greenhouse for the board's own name, got "ABACUS", and reported MISMATCH (code 1). It doesn't read any run report.
  - On the real config, Abacus Insights matched. Ashby and Lever have no name endpoint, so their boards were reported "not checkable", not as passing.
- **Unresolved:** the identity check only covers Greenhouse. A wrong Ashby or Lever board would still finish cleanly.

## 2026-11-10 — Review packet, day 2 live
- **The review test came first.** In `tests/test_review_identity.py`, Claude supplied the setup lines, and the assertions were drafted with Claude's help. I accepted them before any patch existed. The test requires the wrong `abacus` board to make the run `incomplete`, be marked `failed` with a reason naming both employers, and keep its ids out of state. It also requires the right board to still finish. It failed on the old code (`'finished' != 'incomplete'`) and was committed before any fix (`a81c572`).
- **What Claude flagged before patching:**
  - The patch would have to change other existing tests' request counts and fixtures.
  - It would add a rule to the gate.
- **The patch** (`b3f5adb`): a Greenhouse board's own name is checked before its job list is fetched.
  - The name request uses the same error-policy code (moved into a `fetch()` helper).
  - The name comparison is deliberately not shared with `check_identity.py`.
  - In other tests, 17 lines changed: six request counts went up by one, the wrong-version-4 mutant now sends 8 requests instead of 6, and one budget test went from 2 to 3 so it still tests the same property.
  - The review test was unchanged, with 0 changed lines since `a81c572`.
- **My review and decision: accepted.** The review steps ran with AI help:
  - The full suite was run (56 passed).
  - The same real wrong board was run again after the patch (`runs/2026-11-10T170122Z_WRONG-BOARD-after-patch`): `incomplete` after one request, the name mismatch as the reason, and no ids saved.
  - The changed budget test was reviewed. It still verifies that successful boards are saved before the next request would exceed the budget.
- **After the decision:**
  - A dated 2026-11-10 decision was added to `GATE.md` (`7641f93`).
  - **Limit, recorded in the gate:** a valid Ashby or Lever board for the wrong employer could still finish.
  - **Out of scope, left as is:** `loop.run`'s broad `except KeyError` turns any `KeyError` into an "error: config or state" exit, which could hide a real bug.
- **Something I asked during review:** whether we had planned to accept a company's other names. We hadn't. The check only ignores case and punctuation, so "Abacus Insights, Inc." would fail. I left aliases out.
- **Day 2, live** (`runs/2026-11-10T170553Z`).
  - Exit `incomplete`: 5 requests in 1.6 s.
  - The name check ran first and passed. `valonn` got another real 404.
  - Real changes since day 1: Abacus 15 → 16 postings (1 new, "Software Architect"), Xsolla 185 → 186 (1 new), Valon unchanged, nothing closed.
- **Independent cross-check.** `crosscheck_days.py` recomputed new and closed from the two days' raw responses with its own parsing, and it agreed with `run.json` on all three boards.
- **A relisting, not a new job.** The "new" Abacus id `8782226002` was on the board on 10-31 (JS1's saved responses), was gone on 11-09, and came back on 11-10. It is new since the last run, not a first posting, because JS2's state only goes back to 11-09.

## 2026-11-10 — Submission documents
- **Checked against the brief.** The code, gate, boundary cases, runs, traces, raw responses, and this log were in place. `README.md`, the review packet, `SOURCES.md`, and the sign-off with driver's seat were still missing.
- **Claude drafted them** from the commits, the run folders, and our sessions: `README.md`, `WRONG_ANSWER.md`, `REVIEW_PACKET.md`, `SOURCES.md`, and `SIGNOFF.md`. The signature line is left for me.
- **Facts re-checked while drafting:**
  - The review test failed again on a clean copy of `a81c572` (`'finished' != 'incomplete'`), the only failure out of 56.
  - Claude's last code edit for the patch (11:47 ET) came before the after-patch run (12:01 ET), so that run used exactly the code committed in `b3f5adb`.
  - No test covers the Greenhouse name request itself failing. It is now listed under "Not checked."
- **A wording leftover in the gate:** the `error` exit mentions "an invalid persona", but JS2 has no persona. It is listed under "Not checked"; the gate was not amended.
- **Attribution corrected.** The review test's assertions, the after-patch run, and the budget-test review were all done with AI help. `REVIEW_PACKET.md`, `SIGNOFF.md`, `SOURCES.md`, `README.md`, `WRONG_ANSWER.md`, and this log now say so, instead of "I wrote", "by hand", or "I ran".

## 2026-11-10 — Live approval prompt check
- In an AI-assisted terminal session, `python3 agent.py reset-state --state state/seen.json` reached the real y/N prompt: `Approve: drop 233 seen id(s) from state (ashby/valon, greenhouse/abacusinsights, lever/xsolla)? [y/N]`.
- The response entered was `N`. The command exited 3 with `error: not approved`. The state was not reset: `state/seen.json` had 3 boards and 233 seen ids before and after, and its SHA-256 stayed `75ae1028c6fe38d9e9e4df60775d6e0fc996490fb6177307c08e44b1286a572b`.
- For the approval path, `state/seen.json` was copied to `state/approval_yes_demo.json` with the same SHA-256. In a real terminal, `python3 agent.py reset-state --state state/approval_yes_demo.json` prompted to drop 233 ids; the response entered was `Y`. The command exited 0 with `reset state/approval_yes_demo.json`, and the copy now contains `{"board_list": null, "boards": {}}`.
- The original `state/seen.json` still has 3 boards and 233 seen ids, with the same SHA-256 as before either command. Both live prompt responses were exercised with AI help: `N` on the original state, `Y` on a disposable copy.
- `python3 precheck.py` first failed because an ignored macOS `runs/.DS_Store` file was mistaken for a run folder. After removing that Finder metadata file, it returned `precheck: OK`. No program code was changed.
