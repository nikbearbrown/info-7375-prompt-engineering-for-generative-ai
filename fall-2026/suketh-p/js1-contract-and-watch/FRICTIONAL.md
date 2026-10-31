# FRICTIONAL — Job-Search Agent 1

Two parts. **My entries** are in my own words, written while the work happened, and dated. **Claude Code's timeline** is a factual record of what Claude Code did, with times that the commits or saved files can prove. Nothing in the timeline is presented as my experience.

## My entries

### 2026-10-31, after labeling the 20 postings (sent as a draft to review)

The rule is clear, but it is narrower than my actual job interests. Posting 6 has Python and PyTorch, yet fails because its title does not include one of the required focus terms. Posting 20 passes even though it asks for five or more years of experience, since experience is outside the rule. I will keep the rule unchanged for this experiment and report both limits with the results.

_Note added by Claude Code: the posting numbers are positions on [labels/labeling-sheet.md](labels/labeling-sheet.md), so 6 = 4616971008 and 20 = 5418610008. Both statements were checked against the saved posting text: 4616971008 contains "Python" and "PyTorch", and 5418610008 contains "5+ years of experience"._

### 2026-10-31, choosing the one prompt change (v1 had scored 30/30 on development)

A. I want the justification to name the exact résumé and posting fields because I should be able to trace the explanation back to the inputs without piecing it together from the evidence arrays.

I accepted the suggestion to make field names explicit in the justification because that requirement is already in my contract. I am keeping the matching rules unchanged so this experiment tests one change at a time.

### 2026-10-31, after the held-out results

I would switch to v2 because its valid explanations name the fields my contract requires, while continuing to reject malformed replies; the one broken held-out reply remains a failure, and these results do not show that v2 is better overall.

### 2026-10-31, at sign-off

Withheld because the labels supplied in this chat cannot be presented as independent hand labels, and the descriptions of who wrote what need correcting. The statement "before any Claude call" also needs to match the recorded timeline.

### 2026-10-31, after the corrections

Switch to v2 for future runs only, keeping strict validation and leaving runs 1 and 2 recorded as v1. This is a choice for clearer explanations; v2 still missed the experiment's original acceptance condition because one held-out reply was malformed.

_Then, about the corrected drafts: "All are clear, I guess", and "Sign now"._

## Claude Code's timeline (factual)

All times EDT; each line points to the commit or file that shows it.

| When | What happened | Accepted / modified / rejected | Trace |
|---|---|---|---|
| 10-28 06:10 | The student's contract, pasted in chat, was saved to Markdown. A word-and-punctuation check found the same 1,634 tokens in the same order. | Formatting only; wording unchanged | `29b3a26` |
| 10-28 06:10–06:19 | A locked-down `claude -p` probe worked, but carried ~826 input tokens for ~20 tokens of our text. | Raised as a contract conflict for the student to decide | [probes](evidence/probes/2026-10-28-claude-code-probes.md) |
| 10-28 06:19 | 73 tests were written from the contract, plus the wrong versions as code. RED: every module failed to import. | — | `d945f28`, [RED output](evidence/test-runs/2026-10-28-01-red-before-code.txt) |
| 10-28 06:19–06:26 | GREEN 72/73 at first. The W2b wrong version had been written incompletely, so it crashed instead of passing silently. **Fixed the wrong version (test code), not the agent.** | Claude Code's own mistake, corrected | `546fd7a` (commit message) |
| 10-28 06:26 | Run 1, live: 681 postings, 0 new. The raw body was 9.9 MB, so the repo keeps a byte-identical `.gz` plus a `verify` command (tests first). | Packaging decision by Claude Code, listed in README | `78c1b1b` |
| 10-28 06:28 | The real response had four keys the test fixture lacked (`ai_disclaimer`, …), and `metadata` was a list, not null. The fixture was corrected to mirror it. | — | `78c1b1b` |
| 10-28 06:28–06:30 | A probe asking what context Claude Code adds was declined by a safety classifier (`reasoning_extraction`). Not retried or rephrased. | — | [probes](evidence/probes/2026-10-28-claude-code-probes.md) |
| 10-28 06:30 | 20 experiment postings and 5 sampling postings were chosen by seed 20261028, stratified by rule outcome, before any label existed. The labeling sheet hides all rule output. | Selection design by Claude Code | `846c35a` |
| 10-30 00:50 | The student asked what to do next ("I didn't get it"). The asks were cut to four items, and the route question became one choice. | — | chat |
| 10-30 00:50–00:53 | **The student chose the Claude Code login** as the judge route. | Student's decision | chat |
| 10-30 00:53 | Experiment scripts, tests first. Claude Code's own hand-derived expected value was wrong (2, should be 1) and was fixed in the test. | Claude Code's own mistake, corrected | `a61ce00` |
| 10-31 08:49 | The student's Oct 31 contract sentence and labeling rule were saved verbatim. | Student's words | `7752e69` |
| 10-31 08:49 | Seeded agent demo for posting 5418610008: first real Claude call, valid reply, relevant. | — | `a516410` |
| 10-31 08:50 | Run 2, live: 675 postings, 27 new, 27/27 valid replies, 0 disagreements. | — | `a516410` |
| 10-31 08:53 | Surface 2 (Read tool only): relevant, validated. The home path in the saved stream was replaced with `~`. | Privacy edit, recorded in the file | `0f20222` |
| 10-31 09:05 | The 20 labels the student sent in chat were saved verbatim (6 relevant, 14 not), before any sampling or experiment call. They came after run 2, the demo and surface 2. The commit message wrongly says they were made "by reading" the sheet; see the 09:30 row. | Student's labels | `0f312fb` |
| 10-31 09:06 | Labels vs rule records: identical on 20/20 (a consistency check; not independent, see the 09:30 row). The surface-1 reply from the student's chat passed the validator. The chat link was kept out of the repo (privacy rule). | — | `0f3b4af` |
| 10-31 09:06 | Sampling attempt 1 crashed before making any call: the script wrote a file before creating its folder. Fixed with one line; no test was written for that script's file handling. | Claude Code's own bug | `d2db430` |
| 10-31 09:07–09:08 | v1 on development: 30/30 pass. Sampling: 20/20, every posting unanimous. | — | `d2db430` |
| 10-31 09:10 | Claude Code's keyword check for "does the justification cover all four conditions" undercounted: it missed replies that say "Condition 3 (San Francisco…)". It was **discarded, not used as a metric**. A field-path count replaced it (v1: 0/30 justifications name all three posting paths). | Claude Code's own mistake, caught before use | this file |
| 10-31 before 09:14 | **The student chose change A** for v2 (their reason is in PROMPT-EXPERIMENT.md). Their wording, "the exact résumé and posting fields", was wider than the 3 posting paths Claude Code had described, so v2 names all 8. | Student's decision; Claude Code followed the student's wording | `b0d2a88` |
| 10-31 09:15 | v2 prompt and both measures were committed before any v2 call. The first launch failed: zsh did not split `$spec` into words, so argparse refused before any call. The three malformed log files were removed. | Claude Code's own shell mistake | `d5154cd` (message) |
| 10-31 09:16–09:18 | v2 on development: 30/30, traceable 30/30. Held-out, once each: v1 30/30 (traceable 0/30); v2 29/30, one reply with a stray `]` rejected (traceable 29/29). | — | `d5154cd` |
| 10-31 09:22–09:24 | **The student ran all 91 tests in their own Terminal: OK.** Their output was saved, with user and host names masked. Claude Code's own run matched its 91 test lines exactly. | Student's check | [output](evidence/test-runs/2026-10-31-04-student-own-run.txt) |
| 10-31 09:28–09:33 | **The student withheld the sign-off** (reason above, under "My entries"). The record confirms what Claude Code had overstated:<br>• "before any Claude call": false. Run 2, the demo, surface 2 and the 10-28 probes all came before the labels.<br>• "independent hand check": the conversation had shown the rule's relevant list on 10-28, `selection.json` holds each posting's rule category, and both judges' verdicts on 5418610008 were reported before labeling.<br>• The driver's seat credited the student with checks Claude Code did, and SOURCES spoke in the student's voice without saying Claude Code wrote it.<br>All corrected in `5805125`; git history was kept, not rewritten. The student also asked to change the README's test count from 90 to 91. | Student's correction of Claude Code's overstatements, accepted | this file, README "The labels are not independent" |
| 10-31 09:39–09:40 | Two commits made **outside this conversation** by another Claude Code session (each carries the Claude co-author line). `406fb0a` masked the home path in three saved test logs, with a note line in each. `b12ba0c` pushed the branch to the student's fork and checked a fresh sparse clone from GitHub: 91 tests OK, both raw responses verify. This session found them before pushing, read both diffs, and found them accurate. | Accepted after checking | `406fb0a`, `b12ba0c` |
| 10-31 09:42–09:47 | The student reviewed the corrected drafts ("All are clear, I guess"), signed ("Sign now"), switched future runs to v2 (their words are above), and approved the push. Claude Code made the switch test first (92 tests; the student's own run had covered the first 91). It also replaced a test's made-up non-555 phone number with `000-000-0000`, so the test can't contain a real person's number. | Student's decisions | the next commit |
