# FRICTIONAL — JS3 The Filter, the Tool, and the Score

Rithika Sankar Rajeswari. Entries are tied to commits. 
## 2026-11-25 — Starting point (8add55a8, f3c36f07)
- Copied my JS2 folder (4109698); 142 tests passed unchanged. The pull brought in classmates' JS3 folders; I did not open them.
- Froze the real 2026-11-10 board files (Databricks 915, OpenAI 830, Scale AI 169; the 404 board recorded; SEEDED files excluded) in CORPUS.sha256.
- Mistake: `cp -R` also copied JS2's README, SOURCES, SIGNOFF, FRICTIONAL and REVIEW_PACKET. I moved them to `js2-inherited/`, but re-running the move overwrote the real JS2 FRICTIONAL with a new stub. I restored it from the JS2 folder and checked it with `head`.

## FILTER.md before any code (0b6d9df4)
- Confirmed every section. Kept Senior/Staff because JS1 never set a seniority level. Flagged `training` and `model` as possible false friends before measuring.

## First build (4b23b24b, c160bb63, f3bd1b24)
- Claude Code listed 17 ambiguities; I accepted them. One consequence I chose to keep: whole-word matching misses plurals like "models". I ran the 198 tests myself and checked that nothing outside JS3 changed.
- v1.0 kept 70 of 1,914 and reported the 404 board as "not evaluated". Score 3 mixes title-only and body-only matches.
- Committed the blank sheets, then the labeling rule, before any labels existed.

## Labels (dd5aef2a, 45d02190)
- Claude Code built a batch labeler and suggested all 74 verdicts. I paused to reconsider whether the held-out set could still count as independent, then reviewed each suggestion and corrected 9 (held-out rows 8, 14, 15 to unsure, and row 20's reason; audit rows 8, 17, 29, 34, 35, 43, settling 34 and 35 as "not" after seeing the titles).
- The first verdict commit still held Claude's suggestions, and LABELING_METHOD.md still said "not reviewed". The counts gave it away (5 unsure instead of my 7). I fixed both before measuring.
- Reflection: *[Your words: what reviewing the suggestions taught you; the four "excerpt does not establish" corrections]*

## Audit and v1.1 (8d56f9e6)
- 7 of 9 kept postings were wrong. False friend: `ai engineer` matched "Applied AI Engineer" and FDE roles. Added `research engineer` and customer-facing title exclusions. Rejected adding `software engineer` (too broad), knowingly losing audit row 38.
- Errors on the same 50 rows went from 14 to 5, which I recorded as tuning, not as a test.

## Score (31f246b8)
- No version differed on the held-out 24 (2 relevant, 0 kept by any version). The threshold alone moved the kept list from 36 to 133. Both held-out positives were generic "Software Engineer" titles that every version missed. I reported this as a limit.

## MCP (a51179f3, 6519d048, b123ac69)
- The parallel build had not started when I first thought it had; I restarted it.
- Scripted client: 8/8. Claude Code attempt 1 was not connected; it made no tool calls and refused to work around the tool-only instruction. Registration needed absolute paths, and the desktop app's `/mcp` showed no list, so I used the terminal version.
- I accidentally pasted shell commands into Claude Code and it ran them. The server log matched Claude's report exactly. Surprises: an undefined `server/discover` call, and ToolSearch used despite "ONLY".
- The teaching server ignored my first probe (demo mode with no error); I re-ran it with `--stdio`.

## Shortlist (acc4eea5)
- 5 real Claude runs: 21 quotes found, 4 NOT STATED, 0 invented. Claude Code drafted the 25 claim labels; it ran in auto mode although I meant to keep auto off. I reviewed the marked case and the flagged calls.

