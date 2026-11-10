# FRICTIONAL — honest log (my words)

Arundhati K · Job-Search Agent 2 · written 2026-11-10, the day of the work.

How this was written: Claude Code asked me questions in the session; I typed the answers, and Claude pasted
them here unchanged. The *Pointer* and *What happened* lines are facts Claude Code added (commit hashes,
files, times); everything under *My words* is mine.

## Entry 1 — the gate (2026-11-10, ~16:15–16:20 EST)

*What happened:* I asked Claude Code to draft GATE.md ("Claude drafts, I edit") after its explanation of
exits, budgets, repeat rule, error and permission policy. I accepted the draft without edits.
*Accepted / modified / rejected from Claude:* accepted the whole draft, unmodified.
*Pointer:* commit `6833492` (GATE.md, before any code).

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
*Pointer:* commit `6fed708` (predictions), `tests/test_policy.py::BoundaryCases.test_all_16_cases`,
[BOUNDARY-PREDICTIONS.md](BOUNDARY-PREDICTIONS.md).

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
*Pointer:* `a15cbef` (live-1 + demo), `9bb4241` (my approved run), `evidence/logs/02-finished-wrong-answer-demo.txt`,
`tests/test_check.py`.

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
patch (`772af22`); I ran the reproduction, the 43 tests, the diff and an approved live run myself
(`review/02-my-commands.txt`) and decided **accept** (`34ed521`, reason `c9f0653`). I did not run the live
Jasper fetch myself.
*Accepted / modified / rejected from Claude:* accepted the patch unmodified, including the Greenhouse
newline tightening that was outside the Ashby scope.
*Pointer:* `772af22`, `34ed521`, `c9f0653`, [review/REVIEW.md](review/REVIEW.md), `tests/test_providers.py`.

*My words:*
- Running the commands myself helped me see the actual results and errors. Reading Claude's log wasn't enough
  to verify everything.
- I accepted it because the newline change didn't break anything, but next time I'd review unrelated changes
  separately.

## Unresolved

*My words:*
- I still want to check more unusual Ashby board names with special characters and make sure failed boards are
  always reported as incomplete.
