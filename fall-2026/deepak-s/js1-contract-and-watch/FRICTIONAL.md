Drafted by Claude Code from the session record on 2026-10-30, at my request, because I ran out of time.

# FRICTIONAL: honest log

Sources used for this draft:
- the commits (times in ET);
- the logs in private/logs/;
- the Claude Code session record (my messages and its replies, with timestamps).

Claude Code's text is quoted, dated and marked as Claude Code's. Nothing here was written by me as it happened. This file was written afterwards, from that record.

### 2026-10-29 22:10, contract before code
- Tried: commit the contract, acceptance cases 9, 10 and 13, and the test fakes before any implementation.
- Happened: f65f298 at 22:10 and the spec tests (9f315ff) at 22:13 came before the first code (e379a02) at 22:57. Implementing exposed gaps in the contract, which became amendments A1–A6 (61ec8b9, 23:05).
- Checked / changed / learned (incl. unresolved): the contract was silent or ambiguous on the points named in 61ec8b9's message ("labels/source, records, double unescape, stop evidence, judge client"). Each gap became an amendment, not a guess in code.
- From Claude: Claude Code proposed the amendment wording. I decided each one.
- Trace: commits `f65f298`, `9f315ff`, `e379a02`, `61ec8b9`; presubmit check 7.

### 2026-10-30 14:37, no API key
- Tried: the plan assumed the judge would use the Anthropic SDK with an API key.
- Happened: I had no API key. I told Claude Code: "There is no API key. Claude's judgments come from the Claude Code CLI on my subscription. Never set or use ANTHROPIC_API_KEY."
- Checked / changed / learned (incl. unresolved):
  - Claude Code added the `claude-cli` backend. It runs `claude -p` with no tools, in an empty directory, with the key removed from the environment.
  - At 14:40 I chose: a failed CLI call stops the judge, the run finishes and exits 1, and sample and experiment results can be resumed.
  - One smoke call (posting 8172487, 14:46 ET) was accepted.
  - Unresolved: the temperature cannot be set through the CLI. I could not confirm the CLI replaced its default system prompt; that is inferred from about 3.3k input tokens per call.
- From Claude: accepted the backend and amendment A14 as written.
- Trace: commits `17b55ed` (A14), `069dc03` (smoke call, evidence/sampling/20261030T184652Z); `test_a_call_replaces_the_system_prompt_has_no_tools_and_runs_in_an_empty_dir_without_the_key`.

### 2026-10-30 14:59, could a held-out posting be sent twice?
- Tried: I asked Claude Code to confirm from the code, not from memory, that no held-out posting can ever be sent twice under the same prompt.
- Happened: the answer was not "never". Resuming could re-send a held-out posting whose earlier call had errored.
- Checked / changed / learned (incl. unresolved): fixed so that any held-out posting with a saved request is never sent again, with a unit test and amendment A15.
- From Claude: accepted the fix and A15.
- Trace: commit `7ef4622`; `test_a_held_out_posting_with_a_saved_call_is_never_sent_again`.

### 2026-10-30 15:01–15:41, the labels
- Tried: label the 20 selected postings by hand before any Claude call on them.
- Happened:
  - At 15:01 the labels gate failed. Claude Code (2026-10-30 15:01 ET): "Gate 1 failed: `labels/labels.csv` on disk has no labels." The file had not been saved since 14:01.
  - I said "labels done" at 15:35:58, and the labels were committed at 15:36:19.
  - Claude Code (2026-10-30 15:37 ET): "several of your committed labels contradict `labels/LABELING_RULE.md`".
- Checked / changed / learned (incl. unresolved):
  - I labelled quickly, and at least 7 labels contradict my own labeling rule. Examples: Staff, Intern and Manager titles labelled relevant, and a marketing role labelled relevant. Two more contradict it on location (8144196, Chicago) and stated years (8197886, 6+ years).
  - At 15:41 I decided to keep the labels as committed, and to disclose this in the reports and the sign-off.
  - Unresolved: every pass rate measures agreement with these labels, not correctness and not the rule.
- From Claude: accepted Claude Code's report of the contradictions. Keeping the labels was my decision. I asked for a title-only exclusion-agreement check, which Claude Code wrote (scripts/exclusion_agreement.py).
- Trace: commits `533686f` (selection), `251b7b7` (my labels), `a0c5f0b` (split); reports/PROMPT_EXPERIMENT.md, Honest limits.

### 2026-10-30 15:41, sampling: no spread
- Tried: v1, 4 fresh calls each on 5 development postings.
- Happened:
  - All 20 calls were accepted, and all 20 said not_relevant.
  - Agreement with my labels: 0 of 4 on 7983456, 8144196 and 8174963; 4 of 4 on 8175828 and 8191708.
- Checked / changed / learned (incl. unresolved): repeatability is not correctness. The verdicts never flipped, but the citations changed between calls. 7983456 got not_relevant every time, even though my rule says a 5-year minimum fits.
- From Claude: Claude Code ran the calls and drafted the report. The selection rule was fixed before any call.
- Trace: commit `230cb5e`; evidence/sampling/20261030T194141Z/results.json; private/logs/sample.log.

### 2026-10-30 15:44–15:48, one prompt change
- Tried: v1 on the 10 development postings, then one change.
- Happened:
  - v1 scored 3/10 and the rule 6/10.
  - Claude Code proposed two single changes. At 15:47 I picked A: the stated-minimum threshold from my labeling rule.
  - v2 scored 3/10, with 1 rejected: 8194283 cited `/targets/exclude_title_terms/2` for "Intern", but that index is "Director".
- Checked / changed / learned (incl. unresolved): v2 did not beat v1 on development. The validator caught a real off-by-one citation.
- From Claude: accepted option A. Rejected B as tuning toward labels that contradict my rule.
- Trace: commits `3c50b20` (v1), `fcd268a` (prompts/v2.md), `65595bf` (v2); private/logs/experiment_dev_v1.log and experiment_dev_v2.log.

### 2026-10-30 15:50, held-out, once
- Tried: v1 and v2 on the 10 held-out postings, run once.
- Happened: the rule, v1 and v2 each scored 4/10 [0.168, 0.687], with no rejections.
- Checked / changed / learned (incl. unresolved): no evidence that v2 improves on v1. Every interval overlaps.
- From Claude: none beyond running it.
- Trace: commit `7d59b53`; private/logs/experiment_held_out.log.

### 2026-10-30 15:51, run 2, and the second calendar day
- Tried: a second live run with state from run 1.
- Happened:
  - 746 postings, 20 new: 17 agree with the rule, 0 disagree, 3 rejected (the same off-by-one "Intern" citation).
  - Replay exited 0.
  - Run 1 was 2026-10-29 22:58 ET (02:58 UTC on 10-30). Run 2 was 2026-10-30 15:51 ET. That is a different ET date but the same UTC date.
  - I planned a run 3 after 20:00 ET for a second UTC day. On 2026-10-31 at 13:53 I first decided to skip it, then changed my mind before signing.
- Checked / changed / learned (incl. unresolved): all 20 new postings were clear negatives under the rule, so 17/17 is agreement on easy cases only.
- From Claude: none.
- Trace: commits `2453cf3`, `7e44cf8`; private/logs/run2.log; README "What ran".

### 2026-10-30 16:13, my own test run
- Tried: run the full test suite myself, outside the Claude Code session.
- Happened: 228 passed, at 16:13:20 ET.
- Checked / changed / learned (incl. unresolved):
  - The only trace on disk is .pytest_cache/v/cache/nodeids, last modified 2026-10-30 16:13:23 ET. That cache is untracked and not in the submission.
  - The session record has no Claude Code activity between 16:10 and 16:20 ET.
  - The output itself was not saved. "228 passed" is my account.
- From Claude: the tests in tests/spec/ and tests/unit/ were written by Claude Code; cases 9, 10 and 13 are mine.
- Trace: .pytest_cache/v/cache/nodeids timestamp; commit `b787872` (the tree that was tested).

### 2026-10-30 17:41, surface A not run
- Tried: Claude Code prepared the filled prompt for posting 7983456 (private/surface_a_paste.txt, 9,159 characters) for me to paste into a claude.ai chat.
- Happened:
  - At 17:41 I sent back the reply template with its placeholders still unfilled.
  - No chat was ever made, and on 2026-10-31 I decided to describe surface A from analysis only.
- Checked / changed / learned (incl. unresolved): the action-surface comparison has two observed surfaces (B and C) and one analysed surface (A). The "same task three ways" requirement is not fully met.
- From Claude: accepted Claude Code's analysis-only column A, labelled as not run.
- Trace: commit `110e977`; reports/ACTION_SURFACE.md.

### 2026-10-31 13:53, this file
- Tried: I meant to write this log myself.
- Happened: I ran out of time, and asked Claude Code to write it from the session record.
- Checked / changed / learned (incl. unresolved): every entry above comes from a commit, a log or a timestamped message. Nothing in it is my own contemporaneous account, except the 16:13 test result.
- From Claude: the whole draft.
- Trace: the commit that adds this file; SOURCES.md.

### 2026-10-31 14:07, run 3
- Tried: before signing, a third live run, made exactly like run 2 (`--judge claude-cli`, prompts/v1.md). I made it on a date that is 2026-10-31 in both ET and UTC, which Claude Code checked first.
- Happened:
  - 745 postings: 744 previously seen and 1 new, 8327254 (Product Manager, Terminal Payments, Toronto).
  - The rule and the judge agree: not_relevant. Nothing was rejected.
  - The run exited 0, and replay exited 0.
- Checked / changed / learned (incl. unresolved):
  - The two-runs requirement now has a real change on a second calendar day in both ET and UTC.
  - Only one posting was new, and it is a clear negative under the rule (Manager). Run 3 adds no evidence on hard cases.
  - The call took 1 turn, with 0 permission denials and 0 web tools.
- From Claude: none beyond running it.
- Trace: commit `a8c23d4`; evidence/runs/20261031T180716Z_stripe/report.json; private/logs/run3.log; README "What ran".
