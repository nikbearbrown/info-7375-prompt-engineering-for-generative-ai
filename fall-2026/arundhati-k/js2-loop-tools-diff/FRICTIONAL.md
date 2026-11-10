# FRICTIONAL — honest log (my words)

Arundhati K · Job-Search Agent 2 · written 2026-11-10, the day of the work.

How this was written: Claude Code asked me questions in the session; I typed the answers, and Claude pasted
them here unchanged. The *Pointer* and *What happened* lines are facts Claude Code added (commit hashes,
files, times); everything under *My words* is mine.

## Entry 1 — the gate (2026-11-10, ~16:15–16:20 EST)

*What happened:* I asked Claude Code to draft GATE.md ("Claude drafts, I edit") after its explanation of
exits, budgets, repeat rule, error and permission policy. I accepted the draft without edits.
*Accepted / modified / rejected from Claude:* accepted the whole draft, unmodified.
*Pointer:* commit `3055907` (GATE.md, before any code).
*My prompts to Claude:* "start assignment"; chose "Claude drafts, I edit" when asked who writes GATE.md; "Reviewed, commit it".

*My words:*
- I chose Claude to draft because I knew the basic idea but wasn't fully sure about all the rules and edge cases.
- The basic restrictions made sense. Budgets and retries were new to me, and I hadn't thought much about the
  difference between incomplete and finished.
- I would add more examples for edge cases so the rules are easier to understand.

## Entry 2 — my predictions (2026-11-10, 16:24–16:30 EST)

*What happened:* I picked allow / refuse / hold for 16 boundary cases before any test existed. 14 matched the
policy; #12 (write `config/boards.json`) and #14 (state file without the flag) did not.
*Accepted / modified / rejected from Claude:* Claude listed the cases; the predictions are mine. I did not
change them after seeing the results.
*Pointer:* commit `b5381cf` (predictions), `tests/test_policy.py::BoundaryCases.test_all_16_cases`,
[BOUNDARY-PREDICTIONS.md](BOUNDARY-PREDICTIONS.md).
*My prompts to Claude:* "what you can do from it?" (Claude then asked the 16 cases as Allow/Refuse/Hold questions; I clicked each).

*My words:*
- I thought config/boards.json was part of the project, so writing to it seemed safe. I overlooked that writes
  were only allowed inside out/.
- Refuse means block it completely, while hold means wait for my approval. Hold is better here because I can
  review and approve the state-file overwrite if needed.

## Entry 3 — the live run and the finished wrong answer (2026-11-10, 16:35–16:43 EST)

*What happened:* Claude Code ran `live-1` (state held, no flag); I ran `python3 run.py --approve-state-write`
myself (state written). Both: Stripe 775, Figma 143, Notion 155, deliberate board 404 shown as `—`, exit
`incomplete`; `check.py` no findings. The SEEDED demo replayed `live-1` with a constructed empty Figma board:
the wrong version said `finished`, Figma 0 new; `check.py` flagged `finished-with-empty-board` and
`drop-to-zero` (143 → 0); the real agent said `incomplete`, Figma `empty-unverified`.
*Accepted / modified / rejected from Claude:* accepted the demo and the check as built.
*Pointer:* `056f7b8` (live-1 + demo), `402ac73` (my approved run), `evidence/logs/02-finished-wrong-answer-demo.txt`,
`tests/test_check.py`.
*My command:* `python3 run.py --approve-state-write` (my terminal, 16:42 EST).

*My words:*
- Incomplete feels right because one board failed. It shouldn't say finished when not all boards were checked.
- I might have trusted it at first. The incomplete result and the failed board showed that the finished report
  was misleading.
- *Later, same day (corrected after Claude pointed out that Figma was empty, not failed, in the demo):*
  I might have trusted it at first. check.py caught the empty Figma result and the drop from 143 jobs to 0.
  The real agent correctly reported incomplete on the same input.

## Entry 4 — the review (2026-11-10, 16:37–16:50 EST)

*What happened:* Claude Code found that the JS1 board-name rule rejects the real Ashby board `Jasper AI`
(live: 200, 7 postings) and turns the whole run into `error`. It reproduced it and wrote the test before the
patch (`1d4bbbf`); I ran the reproduction, the 43 tests, the diff and an approved live run myself
(`review/02-my-commands.txt`) and decided **accept** (`0067080`, reason `2d4842e`). I did not run the live
Jasper fetch myself.
*Accepted / modified / rejected from Claude:* accepted the patch unmodified, including the Greenhouse
newline tightening that was outside the Ashby scope.
*Pointer:* `1d4bbbf`, `0067080`, `2d4842e`, [review/REVIEW.md](review/REVIEW.md), `tests/test_providers.py`.
*My prompts to Claude:* "accept"; then my reason, typed in chat: "Jasper AI worked after the patch, 3 requests went through, and all 43 tests passed."

*My words:*
- Running the commands myself helped me see the actual results and errors. Reading Claude's log wasn't enough
  to verify everything.
- I accepted it because the newline change didn't break anything, but next time I'd review unrelated changes
  separately.

## Entry 5 — pre-submission recheck (2026-11-10, ~17:00 EST)

*What happened:* I asked Claude Code to recheck everything against the brief before I submit. Reading the code
against GATE.md, it found two places the code did not do what the gate says (the repeat rule compared raw URLs
instead of normalised ones; a permission-policy refusal ended `incomplete`, GATE §1 says `error`) and one GATE §6
wrong version with no test. Tests first (`0c75774e`, failing), then the fix (`af1babf9`): 48 tests pass, no test
edited. It also found that `.gitignore` had hidden the raw evidence from git (fresh-clone check, `4e65c62`).
*My prompt to Claude:* "this time i wish no deduction in marks so can you receheck if evrything is on place".
*Accepted / modified / rejected from Claude:* accepted the fixes.
*Pointer:* `0c75774e`, `af1babf9`, `tests/test_gate_audit.py`, `evidence/logs/03-…`, `04-…`.

*My words:*
- This showed me that even when Claude generates code that looks correct, it can still miss requirements
  documented in GATE.md. I learned that I need to compare the implementation against the actual requirements
  and verify it with tests instead of assuming the code is correct.

## Unresolved

*My words:*
- I still want to check more unusual Ashby board names with special characters and make sure failed boards are
  always reported as incomplete.
