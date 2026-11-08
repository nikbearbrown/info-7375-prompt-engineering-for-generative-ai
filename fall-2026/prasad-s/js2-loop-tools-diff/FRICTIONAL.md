# FRICTIONAL.md

### 2026-11-05 — A number needs its source next to it
- Tried: write GATE.md v0.2 myself, with each board's size in §0.
- Happened: I wrote Duolingo as 57 jobs and Robinhood as 153. My snapshot of the same boards that day, saved in evidence/snapshots/, said 56 and 151, and I hadn't recorded where the 57 and 153 came from.
- Checked / changed / learned: Claude.ai's review spotted the mismatch. I switched §0 to the snapshot's numbers, and GATE's header now names the snapshot as the source ("Written against: … evidence/snapshots/"). Boards change from day to day — Duolingo went from 56 on the snapshot to 59 in run 1 — so a count can only be checked against the saved response it came from. Every number in the gate now points at a file.
- Claude's part: Claude.ai's review flagged the mismatch; the draft, the fix and the choice of source were mine.
- Trace: JS2-CP2, GATE.md header and §0; evidence/snapshots/

### 2026-11-06 — v0.5: two silent losses, caught in review
- Tried: amend CONTRACT.md to v0.5 for JS2, from Claude.ai's skeleton, with my choices. The board key — ATS plus name — was my choice, from two options in the review.
- Happened: my draft of item 8 replaced the four known consequences instead of adding to them, so four pinned cases silently disappeared — the same kind of loss as JS1's deleted required-fields rule. And my isRemote sentence claimed something about all 150 postings when I had seen one.
- Checked / changed / learned: Claude.ai's review caught both. I counted the board with a check Claude.ai wrote — 87 of 150 isRemote, 86 of them Hybrid, 0 location strings saying "remote" — and the sentence now says only what the counts support. With my own grep I confirmed that item 8 lists all seven consequences again. A claim about a whole board needs the whole board counted, and replacing a list is not editing it.
- Claude's part: Claude.ai reviewed both drafts, caught both problems, and typed the fixes as edit blocks, as v0.5's changelog records; I accepted the fixes.
- Trace: JS2-CP4, CONTRACT.md v0.5

### 2026-11-06 — The build amended the contract twice before run 1
- Tried: build the permission layer (CP5a) and the loop (CP5b) against CONTRACT v0.5 and GATE v0.2.
- Happened: the build raised decisions neither file had pinned down, as in JS1's CP3 — Claude Code's own 31 decisions (D1–D11, E1–E20), which I reviewed and accepted. They were settled as CONTRACT v0.6 (from CP5a) and v0.7 (from CP5b) — among them: a seeded board saves no evidence (v0.7 item 1), and a first run with zero jobs saves nothing (item 6).
- Checked / changed / learned: each amendment was committed before the next build step, not after the run it would describe. A contract written before the build is a prediction; the build is where its gaps surface, so the amendments belong before the runs, dated.
- Claude's part: Claude Code surfaced the decisions while building and I accepted them; Claude.ai typed the amendment text for v0.6 and v0.7, as both changelogs say.
- Trace: JS2-CP5a-v0.6, JS2-CP5b-v0.7; CONTRACT.md v0.6 and v0.7

### 2026-11-06 — Ashby blocked the agent's identity
- Tried: smoke-run the loop's fetches before run 1.
- Happened: Ashby answered 403 — Cloudflare error 1010. Python's default identity was blocked, so Notion would have failed in run 1. My curl probe could not have seen it: curl presents a different identity, so the probe passed a door the agent itself could not.
- Checked / changed / learned: I confirmed it with curl, then chose an honest User-Agent over imitating a browser, and the fix was made test-first. A probe only proves what its own identity can do; the agent has to be tested as itself.
- Claude's part: Claude.ai worked through the diagnosis with me and wrote the curl checks I ran; Claude Code made the change, test-first; I accepted it.
- Trace: JS2-CP5c; evidence/tests/cp5c_user_agent_failing_before_fix_2026-11-06.txt; tests/test_user_agent.py

### 2026-11-06 — Run 1: the snapshot is a moment, not a promise
- Tried: run 1, a live baseline across the five boards, with js2nosuchboard failing on purpose. I ran it.
- Happened: the run ended finished — with failures, naming js2nosuchboard, as §1 requires. Duolingo saved 59 ids; the Nov 5 snapshot had 56.
- Checked / changed / learned: the 59 stands. Run 1's state is the baseline run 2 diffs against, and the snapshot was never a prediction of it — boards churn, and a baseline is whatever the first run actually saved.
- Claude's part: Claude Code built the loop (CP5b); the run followed GATE.md as written.
- Trace: JS2-CP6, run 1 report; state/state_2026-11-07T000611Z.json

### 2026-11-07 — Finished, and wrong
- Tried: the CP7 demo — a board with saved ids, an empty response — to see what the loop says when a board with history returns zero jobs. I ran the demo.
- Happened: the board reported ok and the run finished clean. The loop did exactly what GATE v0.2 §4 said — I had chosen option (a) on purpose in the v0.2 review — so the gap was in the rule, not the code. An independent check, not the loop's own report, caught it.
- Checked / changed / learned: GATE v0.3 was written before any patch (CP8a): an empty board with saved ids is a failure. The W5 test came next and failed on the current code (CP8b); only then the patch (CP8c). The order is the evidence — rule, failing test, patch — and none of it was written after the fact. CONTRACT v0.8 (JS2-CP8d) then recorded the User-Agent, GATE v0.3, and the labels, keeping §9's amendment trail complete.
- Claude's part: Claude.ai wrote the demo's commands and the check's commands; I ran both. Claude Code wrote the W5 patch and I accepted it. The demo, the amendment, and the decision are mine.
- Trace: JS2-CP7, JS2-CP8a, JS2-CP8b, JS2-CP8c, JS2-CP8d; GATE.md v0.3 §4 and §6 (W5); evidence/demo_finished_wrong_answer/

### 2026-11-07 — W5's test would have failed for the wrong reason
- Tried: write W5 in GATE v0.3, in my own words, from the CP7 demo — requiring the empty response to be saved as evidence.
- Happened: the demo had seeded Duolingo, and a seeded board saves no evidence (CONTRACT v0.7 item 1). As I drafted it, a test reproducing the demo would have failed for the wrong reason — a missing evidence file — even with the rule implemented correctly.
- Checked / changed / learned: Claude.ai's review caught the contradiction and suggested the live path instead: the test delivers the empty response through the fetch, network patched as in the other loop tests, so evidence really is saved and the rule needs no exception. I chose it. A test has to reproduce its case through the path it claims to test.
- Claude's part: Claude.ai reviewed my draft, caught the seeded-evidence problem, and suggested the live-path test, as GATE v0.3's changelog records; I chose it.
- Trace: JS2-CP8a, GATE.md §6 (W5) and v0.3 changelog; CONTRACT.md v0.7 item 1

### 2026-11-07 — Boundary tests, run by me
- Tried: close out B01–B11, which Claude Code had exercised while building CP5a.
- Happened: I ran them myself and saved the output (CP9b). The results table was written from that output on Nov 8 (CP11), not from the build's claims.
- Checked / changed / learned: a passing test I did not watch is a claim, not evidence. The results table cites output I produced and can re-run, and I checked each row.
- Claude's part: Claude Code wrote the boundary tests and ran them during the build; Claude.ai typed the results table from my output.
- Trace: JS2-CP9b, JS2-CP11a+b; boundary results table