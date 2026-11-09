# FRICTIONAL — Job-Search Agent 2

Two parts. **The student's entries** are the student's own words, dated and placed verbatim; Claude Code adds only the headings. **Claude Code's timeline** (added in later commits) is a factual record of what Claude Code did, with times the commits or saved files can show. Nothing in it is presented as the student's experience.

## The student's entries

### 2026-11-08, before building

November 8, 2026 - Before building

I expect the hard part to be telling the difference between a board with no new jobs and a board I couldn’t check. With two systems, I also need to make sure a posting from one board doesn’t get counted as already seen because it shares a key with another board. I’ll check the saved responses and compare the posting history before and after a run where one board fails.

### 2026-11-08, after the failure run against the saved state

November 8, 2026 — After the failure run

I compared the state file with the copy I saved before the run, then ran the independent checker against the saved responses and both state files. The bad board returned a 404, its job count showed as unknown, and the run ended incomplete with the state file unchanged, just as I expected. I still need to check whether the loop handles a 200 response with an empty jobs list the same way.

## Claude Code's timeline (factual)

Times are EST. Unmarked times come from commits, file save times, or the runs' own clocks. **Times marked ~ are approximate**, placed from the conversation, which stays on the student's machine (brief, "Privacy and boundaries"). "Decided by" names who settled each item.

| When | What happened | Decided by | Trace |
|---|---|---|---|
| 11-08 04:20 | Before any gate existed, Claude Code probed 12 board URLs (read-only). 9 answered; made-up names got 404 on both systems; Greenhouse `hubspot`, an empty board in Lectern's notes, now got 404 | — | [evidence/probes/](evidence/probes/2026-11-08-board-probe.txt) |
| 11-08 04:22 | Gave the student a worksheet: the brief's questions, the probe's facts, and "cases to decide" posed as questions | — | [sheets](evidence/sheets-given-to-the-student/README.md) |
| 11-08 04:51 | Timed the downloads the gate's 5 s limit applies to: Anthropic and Databricks (about 10 MB each) in 0.50–0.59 s; Linear (0.45 MB) in 0.13–0.24 s | — | [timing](evidence/probes/2026-11-08-board-timing.txt) |
| 11-08 04:52 | Before any code: the student's GATE.md committed byte-for-byte, and their first entry verbatim | Student | `b55d2a5` |
| 11-08 ~04:55 | Two readings of the gate put to the student. Wrong-run or wrong-file approval → **incomplete**. Later (~05:21): a redirect → **unverified, keep going** | Student | `7db4ab4` message |
| 11-08 05:20 | The student's 21 predictions committed before any policy code or test | Student | `f871ccb` |
| 11-08 05:22 | 12 JS1 files copied unchanged (identical blobs). One JS1 test pins an empty board as valid | — | `d133453` |
| 11-08 05:34 | Tests from GATE.md, RED: the 30 carried tests pass; the new modules don't exist yet | — | `7db4ab4` |
| 11-08 05:42 | The agent, GREEN 154 on the first run. Before that commit, Claude Code found that two of its own wrong versions called the function they replace (infinite recursion once swapped in) and fixed them | — | `208d1e3` |
| 11-08 05:44 | Reading `http.client` after GREEN, Claude Code found that a trickling or stalled body could overrun the 5 s request limit. Its first stall test **passed on the old code** (too weak). It was strengthened, then failed as it should | — | `431ac57`, both runs kept |
| 11-08 05:45 | Fixed (`read1`, timeout renewed before each receive): GREEN 158 | — | `5d8bc8c` |
| 11-08 05:45 | First live run with the deliberate failure, run by Claude Code: incomplete, no state | — | `252e84d` |
| 11-08 05:46 | `trace.md` put the exit status in the HTTP column. Fixed for later runs; the run's own files were kept as written | — | `8020acb` |
| 11-08 05:47 | SEEDED finished-wrong-answer: an empty Linear body ended `finished`; the independent check flagged it | — | `ecd83b7` |
| 11-08 06:17 | The student's approved normal run: finished, first state saved | Student typed the approval | `0507a83` |
| 11-08 06:19 | The student's failure run against the saved state: incomplete, `cmp` unchanged, check PASS | — | `72195da` |
| 11-08 06:23–06:50 | The student's review gate and second entry committed before any test or patch | Student | `64357fe` |
| 11-08 ~06:52 | Claude Code proposed a third reproduction (all boards empty) | Student: **adopted** | `a61f07e` message |
| 11-08 06:53 on | The student's first two test runs failed to import: the file was not in the JS2 folder. `find` showed a same-named file only in another student's folder (not opened) | — | [their output](evidence/test-runs/2026-11-08-04x-student-review-test-not-found.txt), [SOURCES.md](SOURCES.md) |
| 11-08 07:16–07:29 | The student's test, v1 (their own RED run), then v2 with the adopted case (Claude Code's RED run) | Student | `2eb4a5f`, `a61f07e` |
| 11-08 07:30 | Claude Code's plan, before any edit | Student checked it against the scope | `231c4cf` |
| 11-09 00:09–00:10 | The student's request; Claude Code's 2-line patch; no test run on it by Claude Code | Student asked | `4dccaee`, `4e39762` |
| 11-09 00:35–00:37 | The student ran the tests (00:35:50), saved the audit (00:36:08) and the decision (00:37:32): **accept**. The record shows the audit saved after the tests began; the student's decision says so | Student | `82739cd` |
| 11-09 00:41 | Full suite on the patch (163 OK) and the seeded demo rerun (now incomplete, check PASS), both by Claude Code after the decision | — | `11bd1f6` |
| 11-09 00:43 | Boundary table generated by running every case through the real policy: 21/21 predictions match | — | `632c78d` |
| 11-09 00:45 | Claude Code's coverage search found the CLI checking one path without the policy. Its first test **passed on the old code** (too weak); strengthened; fixed. 164 OK | — | `c17621e` |
