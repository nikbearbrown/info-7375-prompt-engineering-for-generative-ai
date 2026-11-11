# FRICTIONAL — JS2 Loop, Tools, and Diff

Rithika Sankar Rajeswari. Entries are tied to commits, not clock times.
Fact lines are from my running notes and terminal output. 

## 2026-11-10 — Starting point (b9ede94)
- Copied JS1 (aa7c870) into a new folder; the 42 JS1 tests passed unchanged.
- `git pull` brought in classmates' JS2 folders. I decided not to open them.
- Checked boards in the browser first: Scale AI 169, Databricks 916, OpenAI (Ashby) has no total field.
- The 404 body says "Job not found", not "board not found", so the agent has to decide by status code, not message text.
- Reflection: I didn't open classmates' folders because I wanted my gate decisions to be my own before seeing anyone else's. If I had read theirs first, I couldn't honestly say which choices were mine.

## 2026-11-10 — Gate before code (d761cc3, 7af9366)
- Wrote GATE.md one section at a time; I accepted the proposed values.
- Signed it "10/11/2026", which reads as October 11. Changed to 2026-11-10.
- My first FRICTIONAL.md commit was empty: I hadn't saved the TextEdit edit.
- Reflection: The decision I'd defend is that a failed board reports new jobs as "unknown", never 0. A 0 looks like "nothing new here", so Priya would stop checking that company. "Unknown" tells her to go look. The demo later showed the same danger from a different direction.

## 2026-11-10 — Build by Claude Code (e9d8ef1, 82e67f8)
- Claude Code pointed out my budget reasoning was wrong (4×20 + 2 + 20 = 102 s > 90). Kept 90, corrected the reasoning.
- It also showed B04 didn't catch an "ends with" host check, so I added B20.
- The symlink mutant needed the macOS /var → /private/var workaround.
- Ran the 134 tests myself instead of trusting its count.
- When saving its summary, it reworded it; I replaced it with the verbatim text.
- Filled the boundary-test results by script from the saved test log, not by hand.
- e9d8ef1's message claimed B20 and the budget fix, but they weren't in it. Caught it because the script printed no B20; fixed in 82e67f8.
- Reflection: A commit message is a claim, just like Claude Code's summary, and this time the wrong claim was mine. Now I check what a commit actually contains (`git status`, the diff, the script output) before I trust its message, including my own.

## 2026-11-10 — Live run 1 (3749c43)
- Exit `incomplete (1)`, as predicted. The deliberate 404 was sent once, not retried, state not updated — I checked this in trace.jsonl.
- Databricks went from 916 (browser, earlier) to 915 (run).

## 2026-11-10 — Finished-wrong-answer demo (5e49e71)
- First day-2 attempt got the same run ID as day 1 (same second). The policy refused to overwrite day 1's trace; exit `error (3)`. Kept it as evidence.
- Reran after `sleep 2`: `finished (0)`, Scale AI 0 new. The independent check flagged it.
- Reflection: What bothered me was how normal the wrong run looked: exit 0, a clean report, no warning anywhere. If I hadn't had the independent check, I would have believed it. That is why I withdrew the known limit instead of just documenting it.

## 2026-11-10 — Review packet (b8a5df3, 7de028b2, 764ac2f6)
- Withdrew the known limit I had accepted in GATE §4, because of the demo.
- Predicted the review test: test 1 fails, test 2 passes. That's what happened.
- Claude Code stopped and asked to change a checker test outside the allowed list. I said yes before seeing the edit, then read it.
- My first approval screenshot wasn't saved (I had only dragged it into the chat); retook it at 2:56 PM.
- Worried the buggy run had emptied Scale AI's state. It hadn't: only the "updated" field changed.
- Pasting diff output into Terminal created an empty file named `updated:` (zsh read `>` as a redirect). Found and deleted it before committing.
- Reflection: What I'm still unsure about: no test runs an Ashby board through the new rule, so I'm trusting the shared code path without proof. The rule also only fires on exactly zero, so a drop from 169 to 1 would still look fine. And the fix has only been checked on SEEDED data and fakes, not on a live board that actually went empty.

## Assistance
- Claude Code (Northeastern): wrote the loop, policy, adapters, transport, checker, tests, mutants, the --boards option, and the patch.
- Claude (chat): proposed GATE.md wording, the boundary-test table, the review test draft, the review packet draft, and the reflection drafts in this file; guided terminal steps.
- Me: every decision in GATE.md, the predictions, running every test and live run, reading the diff, the accept decision, and reviewing and editing every reflection.
