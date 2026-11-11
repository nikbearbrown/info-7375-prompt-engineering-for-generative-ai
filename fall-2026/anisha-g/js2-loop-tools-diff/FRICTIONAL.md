# FRICTIONAL — Job-Search Agent 2
Anisha Gaikar. Times are 2026-11-09, Eastern. Claude (this chat) drafted the factual entries from what happened in our session; entries marked **(my own words)** are mine.

## Commits so far
| Commit | What |
|---|---|
| cdc62ba | GATE.md alone, before any code |
| c60940c | My boundary predictions + tests, before any implementation (`logs/00_tests_before_any_code.txt`: they fail at import) |
| 3ac13df | Removed files from a second, parallel draft that had been created in the folder |
| (next) | Implementation (stage B) + logs 01–03 |
| (next) | This attribution correction |

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
