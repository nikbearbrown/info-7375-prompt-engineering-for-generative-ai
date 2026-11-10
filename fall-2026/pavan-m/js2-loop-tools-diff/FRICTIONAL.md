# FRICTIONAL — Job-Search Agent 2

## Entry 1 — November 9, 2026: Starting point
Started from my own JS1 (../js1-contract-and-watch, submitted at 9b381ec), copied unchanged into this folder so JS2 runs on its own from a fresh clone and JS1 stays untouched. The first copy failed 1 test because I forgot JS1's prompts/ folder; after copying it, 9/9 passed. Committed as 9b66b8d. Added .DS_Store to .gitignore (JS1 grader feedback).
Python is now 3.14.3 (Homebrew, venv created with conda deactivated) instead of JS1's 3.14.6 from Anaconda.
An earlier read-only Claude Code session pointed out that JS1's `_usable_id` accepts only integer ids, so Lever/Ashby postings (string ids) would be dropped. Candidate defect for the review packet.

## Entry 2 — November 9, 2026: Choosing and checking the boards
On Nov 8, I ran curl (commands suggested by Claude Code) and saved OpenAI (Ashby, 816 postings) and Palantir (Lever, 305). Today, I captured all four boards myself:
- Glean, Greenhouse: 200, 123 postings
- Palantir, Lever: 200, 304 postings (a plain JSON list, no "jobs" key)
- OpenAI, Ashby: 200, 825 postings
- pavan-js2-no-such-board, Greenhouse: 404, {"status", "error"}: the deliberate failure
Chose these 3 real boards on 3 systems plus 1 deliberate bad name. The counts changed between Nov 8 and Nov 9, so the boards do change from day to day.

## Entry 3 — November 9, 2026: GATE.md written before any code change
Wrote GATE.md: boards, exits, budgets, repeat rule, error policy, permission policy, 12 wrong versions. Review with Claude found three gaps I fixed before committing: the finished-wrong demo could never end "finished" while the bad board is in the config (added a separate demo config); the write policy allowed only out/ but JS1 writes state/ and evidence/ (added an explicit out/ layout); and two outcomes were undecided (a retry blocked by the budget, and a refused redirect from a remote board). Also changed "normalized URL" to "identical URL string", made 429 an explicit no-retry row, and replaced a claim I couldn't test (symlink swap between check and write) with a stated known limit.

## Entry 4 — November 9, 2026: Policy tests written before implementation
Wrote the asserts for 16 policy tests (tests/test_policy.py), one per row of BOUNDARY_TESTS.md, before agent/policy.py exists. Network tests check that refused requests were never sent (not only that an error appeared); write and reset tests check that files are unchanged after a refusal; B5 checks that an allowed GET still works, so a block-everything client can't pass. First run: ModuleNotFoundError for agent.policy (expected).

## Entry 5 — November 9, 2026: Loop tests written before implementation
Wrote the asserts for 13 loop tests (tests/test_loop.py) before agent/loop.py or check_run.py exist: exits (finished vs incomplete), no invented zero for a failed board, no retry on 404, exactly one retry with a 2-second wait on 5xx, request and time budgets stop before sending, a retry blocked by the budget, duplicate board repeat_blocked, failed board's state unchanged, baseline then only new ids with no collision across boards, raw + trace saved inside out/runs/, and the independent checker flagging an empty board the loop reported as finished.
Decision: no string-id test yet. I want the JS1 integer-only id bug to surface on real Lever/Ashby data first, so it can be reproduced and fixed test-first in the review packet.

## Entry 6 — November 9, 2026: Claude Code built the policy, adapters, loop and checker
Claude Code wrote agent/policy.py, agent/adapters.py, agent/loop.py, check_run.py and config/. Verified myself: `python -m pytest -v` → 38 passed (9 JS1 + 16 policy + 13 loop); `git diff tests/ GATE.md BOUNDARY_TESTS.md` empty.
Reviewed its 19 undecided choices. Accepted most. Two changed GATE.md's meaning (https-only; reset reports all postings as new instead of a fresh baseline), so I added a dated revision to GATE.md, admitting it came after the code. Accepted three known gaps instead of fixing them tonight: redirect hops vs the budget check, a slow trickling response vs the time budget, concurrent runs.
As instructed, it reused JS1's _usable_id unchanged; postings that fail it are counted as unusable_ids.

## Entry 7 — November 10, 2026: Real run #1 (live, all four boards)
Ran the loop live at 10:25 AM EST (out/runs/2026-11-10T102543/; terminal saved as evidence/run1_terminal_2026-11-10.txt). Status incomplete, 4 requests, ~2 s. Glean: baseline, 123 postings, all usable. Deliberate bad board: failed, bad_board, HTTP 404, postings null (no invented value).
Defect reproduced on real data: Palantir (Lever) 304 of 304 ids unusable, OpenAI (Ashby) 826 of 826 ids unusable. JS1's _usable_id accepts only integers, and these ids are string UUIDs. The loop still wrote state for those boards with no ids, so after a fix, their next run would report every posting as new.
Mistake in my own check: I printed `$?` after `| tee`, so "exit code: 0" was tee's exit code, not the agent's. summary.json says exit_code 1; still to verify properly.
Missed my plan to run before midnight on Nov 9, so agent runs are all on Nov 10. The Nov 8 and Nov 9 manual captures are the earlier days.

## Entry 8 — November 10, 2026: Review packet, defect reproduced and test written before the patch
Reproduced the defect twice before any fix: live in run 1 (Palantir 304/304, OpenAI 826/826 ids unusable), and on identical saved input with config/replay_nov9.json (Palantir 0/304 usable, OpenAI 0/825 usable; evidence/review/1_replay_BEFORE_patch.txt). The agent's exit code for that replay was 0 (finished), checked without tee this time.
Wrote tests/test_string_ids.py: string ids are kept and new ones detected; empty or missing ids still unusable. Both fail before the patch (assert 0 == 1; evidence/review/2_test_FAILS_before_patch.txt).
Changed my first draft of the second test after review with Claude: the bad postings now have the same shape as real ones except for the id, so they can only fail for the id reason.

## Entry 9 — November 10, 2026: Review packet, patch revised then accepted
Claude Code's first patch fixed the id rule in JS1's shared _usable_id (watch.py). Tests passed, but reading the diff as behavior, it also changed JS1's code path and (as Claude Code itself reported) could crash JS1's state write on mixed int/str ids. I rejected that scope and asked for a revision: same rule, applied only in the JS2 loop path. v2 changed only agent/adapters.py; watch.py is back to JS1. 40 tests pass. On identical Nov 9 input, usable ids went from 0/304 and 0/825 to 304/304 and 825/825. Accepted v2.
Still missed by my tests: whitespace-only ids, and no UUID format check.

## Entry 10 — November 10, 2026: Removed the two empty state files by hand
Run 1 (before the string-id fix) wrote state for lever:palantir and ashby:openai with seen_ids: [], because every id was dropped. After the fix, the next live run would have reported all ~1,130 postings on those boards as new. An approved reset wouldn't help, since it also writes seen_ids: []. I removed both files myself with `git rm`, so their next run is a fresh baseline. GATE.md forbids the agent from deleting files; this was my own action, done in a separate commit so it is visible. Glean's state was kept.

## Entry 11 — November 10, 2026: Real run #2 (live), real new postings found
Ran live at 1:12 PM EST (out/runs/2026-11-10T131257/; evidence/run2_terminal_2026-11-10.txt). Status incomplete, agent exit code 1, this time checked properly without tee. 4 requests.
Glean: compared with run 1's state, 125 postings, 2 new:Designated Technical Support Engineer; Designated Technical Support Engineer. This is the first time my agent detected a real new posting on live data, which JS1 never did.
Palantir: fresh baseline, 304/304 ids usable. OpenAI: fresh baseline, 829/829 usable (826 at 10:25 AM). Bad board: failed, bad_board, HTTP 404, postings null.

## Entry 12 — November 10, 2026: Finished-wrong-answer demo
Built a CONSTRUCTED empty Glean response from my real Nov 9 capture and a demo config with three replayed boards (no bad board). The loop ended finished, exit 0, reporting Glean as ok with 0 postings: clean and wrong. check_run.py flagged it as a suspicious empty board (exit 1), and found 0 problems on real run 2 (exit 0). Limit noted: the checker flags any empty board and doesn't catch a large drop that isn't to zero.