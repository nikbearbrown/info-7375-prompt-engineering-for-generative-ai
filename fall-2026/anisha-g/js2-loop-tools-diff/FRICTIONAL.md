# FRICTIONAL — Job-Search Agent 2
Anisha Gaikar. Times are Eastern, 2026-11-09 unless marked 2026-11-10. Claude (this chat) drafted the factual entries from what happened in our session; entries marked **(my own words)** are mine.

## Commits so far
| Commit | What |
|---|---|
| cdc62ba | GATE.md alone, before any code |
| c60940c | My boundary predictions + tests, before any implementation (`logs/00_tests_before_any_code.txt`: they fail at import) |
| 3ac13df | Removed files from a second, parallel draft that had been created in the folder |
| 596fc0f | Implementation (stage B) + logs 01–03 |
| 24ed508 | Attribution correction |
| c2afaa4 | 17 tests for the reviewers' findings, before the fixes (`logs/04`: they fail) |
| 8be479f | Fixes; 64/64 pass |
| d3f9778 | Live runs 1 and 2, two finished-wrong demos, independent checks |
| 21451f2 | Review packet: defect reproduced, the test fails before the patch |
| (final) | Review packet accepted, plus the write-ups |

## Log
**~2:56 pm** — My JS1 grade was 84/100: all 80 criterion points, but Relative Quartile 4/20. The grader's note: write the gate yourself before Claude starts. I decided to commit GATE.md alone, first.

**~3:02 pm** — I answered the gate questions. ChatGPT drafted the wording of my answers; I read them, changed some, and chose what to keep. Claude copied them into GATE.md unchanged.

**~3:08 pm** — Committed GATE.md alone as `cdc62ba`, before any code.

**~3:13 pm** — I gave my 17 boundary predictions (again worded with ChatGPT's help) and kept the four suggested boards. Claude recorded them in PREDICTIONS.md.

**~3:17 pm** — Committed the tests before any implementation (`c60940c`). The failing log shows `errors=4`, not 3: the 4th came from a parallel draft that Claude Code on my Mac had started in the same folder (`tests/test_boundary.py` and 5 other files) and that `git add -A` picked up.

**~3:19 pm** — Removed that parallel draft (`3ac13df`). Decision: one builder (this Claude chat); Claude Code on my Mac only reviews.

**~3:20 pm** — Finding while writing tests: with 5 boards and one retry each, at most 10 requests are possible, so my 15-request limit can never be the binding one, and my wrong-version-2 scenario ("request 15 times out") cannot happen at my real numbers. The tests check it at a smaller limit.

**~3:23 pm** — My decisions:
- Keep 15 requests as a safety cap: "Five boards with one retry each can use up to 10 requests. The extra five leave room for redirects that pass the permission check. Every request counts toward the cap, and the 60-second limit still applies."
- Keep the apply-URL test: "That tests whether the agent checks the endpoint's purpose as well as the hostname and HTTP method."

**~3:30 pm** — I had stage B reviewed by Claude Code on my Mac and by ChatGPT. Both confirmed 47/47 tests pass and both wrong versions are caught. They found real problems the tests missed. The most serious:
- A valid empty list wipes the seen ids, so the next run reports every job as new (Claude Code).
- Redirects bypass the 15-request cap (both).
- The report folder itself being a symlink lets writes escape (ChatGPT).
- The independent check only re-reads the agent's own saved files (Claude Code).

**~3:35 pm** — Attribution correction. ChatGPT said it drafted the wording of my gate answers and predictions, but both files said "my own words". I corrected both files to say so (choice A, my decision). The original lines stay in git history (`cdc62ba`, `c60940c`).

**~3:38 pm** — My decision for the review-packet defect: "Keep the IDs. A valid empty list tells me the board has zero postings right now. It doesn't erase what the agent saw before…" (full text in REVIEW-PACKET.md §1).

**~3:40 pm** — Claude wrote 17 tests for the other reviewer findings and froze them (`tests.review-fixes.frozen.sha256`), then wrote the fixes. I didn't run anything after this until the next day. **Unresolved that night:** nothing was committed yet past the tests.

**2026-11-10, ~9:29 pm** — I came back with 2.5 hours left before the deadline. GitHub still ended at `3ac13df`.

**~9:30 pm** — Ran one command that made 4 commits in order:
1. the stage B code (its logs show 8 and 2 failures on the wrong versions, then all tests passing);
2. my attribution correction;
3. the review-finding tests, failing (`failures=6, errors=11`);
4. the fixes (64/64).

The push was rejected once because classmates had pushed; `git pull --rebase` fixed it.

**~9:31 pm** — Live runs on my Mac:
- **Run 1:** klaviyo 145 jobs, datadog 394, palantir 304. `no-such-board-7375` got HTTP 404, so the run was `incomplete`. 4/15 requests, 2.3 s.
- **Run 2,** 7 seconds later: the same, 0 new.
- **Independent checks** with a live curl recount: PASS.
- **Demo A** (404 shown as 0 jobs) and **demo B** (a Lever parser bug, palantir shown as 0 jobs) both ended `finished` and both were caught by the check: FAIL, naming the 404 and the 304 jobs.

**~9:34 pm** — Review packet: committed the test while it failed (`21451f2`, `logs/20`: `failures=2`, the returning jobs 1 2 3 reported as new).

**~9:35 pm** — Asked Claude Code on my Mac to make the smallest change in `watch.py` and not touch the tests. It changed one line, to add ids instead of replacing them. I saved the diff (`logs/21`) and ran the tests myself: 2/2, then 66/66 OK (`logs/22`, `logs/23`).

**~9:40 pm** — Decision: **accept**. Claude (this chat) pointed out that my first two answers about the decision said "I haven't seen that output here", although the output was on my screen. So I gave the decision again, after looking at the logs myself.

**(my own words)** I was surprised that a board could return a valid empty list and still expose a bug. The empty run looked fine. I only saw the problem on the next run, when returning jobs were counted as new.

**What I accepted, changed or rejected from Claude, Claude Code and ChatGPT:**
- **Accepted:** Claude's code and tests, and Claude Code's one-line patch, after the evidence.
- **Changed:** I kept 15 as a cap, not lowering it to 10, and kept the apply test. After the reviews, my independent check gained a live recount.
- **Rejected:** Claude Code's parallel build in my folder (removed), and ChatGPT's answers that claimed things it could not see.

**~9:43 pm** — I chose my three "Not checked" items (1, 2 and 3: only 3 real boards; no real timeout, blank body or redirect happened live) and wrote my driver's-seat reasons. Claude put them in the README word for word.

**~9:47 pm** — Final review by Claude Code on my Mac found 4 things:
1. My review decision quoted "your local output", which reads as someone else speaking. The packet now records only my decision (accept) and the evidence from my own logs 20–23.
2. An empty driver's-seat cell. Removed the row; only the loop and review rows are required.
3. The README overstated what I reused from JS1: I reused the ideas, not the code. Fixed.
4. **A real test gap:** the wrong Lever parser passed every unit test, and only the independent check caught it. Claude added `tests/test_parsers.py` **after** the code (labelled so), and `logs/24` shows it failing on that wrong version.

**Unresolved (I know about these and didn't fix them):**
- Old snapshots that were already wiped by the old code stay wiped, so an old posting can be flagged as new one more time.
- The seen set now grows forever, with no limit.
- No real timeout, blank body or redirect happened live; those paths were tested only with fakes.
