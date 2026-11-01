# FRICTIONAL — Anisha Gaikar, JS1

**2026-10-31, ~5:07 pm** — Started on the due date. Asked Claude to build the assignment and ask me for what it needed. Claude couldn't reach any job-board API from its workspace (all three hosts refused by its proxy), so every real run happens on my Mac.

**2026-10-31, ~5:10 pm** — Picked defaults when asked: Klaviyo's Greenhouse board (same company as my Reallocation recipe), a new fictional persona, and the rule title + ≥2 skills + ≤3 years. Claude reused the HTML cleaning from my own `fetch-board.py`.

**2026-10-31, ~5:12 pm** — Claude's tests passed in its workspace (9 tests) and a fake-board / fake-Claude smoke test ran every command. Not yet run on real data.

**Honest note on order:** the assignment says to write CONTRACT.md before asking Claude to write anything. I did not: Claude drafted the contract and the code together at ~5:10 pm, and I committed the contract at ~5:37 pm, before any run, test or label. So the contract came before every run and result, but not before the code.

**2026-10-31, ~5:37 pm** — Asked Claude to write the failure sentence; it drafted one, I read it and committed the contract as `9af05ef` before running anything (after `git pull --rebase` the same commit is `509e6ca`).

**2026-10-31, ~5:38 pm** — Tests: 9 passed on my Mac. Run 1 (live, baseline): 156 postings, 0 new — correct for a baseline.

**2026-10-31, ~5:39 pm** — The label sheet came out with only **6** postings: Klaviyo had only 6 analyst/analytics titles, not 20. Claude patched `labels` to take all 6 analyst postings plus 14 random others (seed 7375). Accepted: it also gives the set clear negatives.

**2026-10-31, ~5:41 pm** — My first labelling attempt broke: pasting a script into Terminal left it stuck (`heredoc>`, `dquote>`), and the script couldn't read my typing through a heredoc. Claude rewrote it as `label.py`; I opened a fresh Terminal window. I hand-labelled all 20; I stopped once at #13 and found #12 (Manager, IT SOX) had the wrong reason pasted, so I fixed it, and Claude changed `label.py` to resume where it stopped. My labels: 19 `not_relevant`, 1 `relevant` (Senior CS Compensation Analyst).

**2026-10-31, ~5:55 pm** — Ran the experiment and sampling on my Mac: **all 60 Claude calls came back empty** and were rejected as `INVALID` by my validator — the validator did its job. Cause: `claude -p "Reply with only the word OK"` → "You've hit your individual spend limit" (exit 1). My Claude Code could not make any more calls tonight.

**2026-10-31, ~5:58 pm** — Decision: I sent Claude my run-1 raw response; Claude rebuilt the same 20-posting sheet with the same seed (it checked the ids and order matched mine exactly) and entered my labels as I had typed them, then ran dev, held-out and sampling with `claude -p` in its own workspace (each call a fresh conversation). Same code, same prompts, same raw data; only the machine differs. Unresolved: these Claude calls did not run on my machine.

**2026-10-31, ~6:00 pm** — Results: revised prompt 10/10 dev, 9/10 held-out; baseline 8/10 and 5/10, mostly from INVALID format (unknown `resume_fields`, and quoting the location line, which my validator rejects because it only checks title + body — a validator strictness I found, not a Claude invention). Sampling: 20/20 valid, 4/4 the same verdict on every posting — and 4/4 `not_relevant` on the one posting I labelled `relevant`.

**2026-10-31, ~6:05 pm** — Claude looked into that disagreement for me: the posting says "3–5 years"; my rule takes the top of the range (5 > 3). I read it as reachable at 3. Not changed tonight — logged as "not checked" in the sign-off.

**2026-10-31, ~6:05 pm** — Run 2: I didn't expect the board to change within the evening, so Claude did the seeded run in its workspace the assignment allows (run 1's real response minus its 3 newest ids, then the real response): 0 new, then exactly those 3 new, judged by both rule and Claude (all `not_relevant`, all valid).

**2026-10-31, ~6:12 pm** — Before submitting, I asked Claude to check my folder against the assignment. It found 3 gaps:
1. I had only written the action-surface table; I had not actually done ways 1 and 2.
2. The persona was checked only by a test, not by the agent itself.
3. My driver's seat said Claude did "nothing" with my labels, but it had copied them into its workspace run.

Fixes: Claude ran ways 1 and 2 for real with `claude -p` (`reports/action-surfaces/`). `load_resume` now refuses a non-fictional résumé, with a new test (10 tests pass). The driver's seat row now says what Claude did.

**2026-10-31, ~6:17 pm** — I asked Claude to compare my folder with classmates' folders in the course repo (structure only). It found that they kept every raw Claude reply. My 6:00 pm experiment and sampling files kept only the verdicts. Claude changed `agent.py` to save each raw reply with its timestamp (`raw_reply`, `at`), and reran dev, held-out and sampling with `claude -p` in its workspace. The 6:00 pm verdict-only files are kept in `reports/first-run-1800-verdicts-only/`. The rerun matched the first run except for the baseline on held-out: 6/10 (3 INVALID) instead of 5/10 (4 INVALID). The same prompt gave a different format-failure count on a second try, which is more evidence that one run of ten cases is a weak measurement.

**2026-10-31, ~6:26 pm** — In a grader-style review, Claude found that my run-1 report file was empty (0 bytes; the cause is unknown; the original was not recreated, but a labelled reproduction was added at ~6:35 pm, see below). Claude also found that the README's seeded-run command would delete my live `state/seen.json`. Claude's patch fixed the command, and I ran a real live second run on my Mac with the rule judge only: `2026-10-31T182630-live: 156 on board, baseline=False, new=0 -> runs/2026-10-31T182630-live-report.json`.

**2026-10-31, ~6:35 pm** — After a second grader-style review by Claude, I corrected the sign-off, SOURCES and this log wherever they said I did something Claude did. I added worked examples to the contract as a dated appendix (the rule is unchanged), and added a labelled reproduction of run 1's empty report from its saved raw response.

**2026-10-31, ~6:38 pm** — Honest note on labelling: my labeling rule says to read the whole posting, but in practice `label.py` showed me the title, location, link and up to 8 lines that mention years, skills or a degree, and I did not open every link. I listed this under "Not checked" in the sign-off.

**What I accepted / changed / rejected from Claude:** accepted the code, tests, prompts and doc drafts; changed the label sampling (6 → 20 postings) and the labeller after it failed; rejected letting Claude write the hand labels — those are mine. Claude also drafted most of this log from what happened in our session; I read it before submitting.



**2026-10-31, ~6:55 pm (my own words)** — I pasted way1-prompt.txt into a new claude.ai chat myself; the screenshot is reports/action-surfaces/way1-ANISHA-screenshot.png. Claude said "Mostly not relevant", a weak match: the skills overlap, but it's a senior compensation-operations role asking for 3–5 years. What surprised me: ____. Next time I would ____. What I still don't fully understand: ____.
