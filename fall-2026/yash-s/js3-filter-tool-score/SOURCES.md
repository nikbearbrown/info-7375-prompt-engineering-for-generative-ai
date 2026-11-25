# Sources and AI use

## What I started from

My own JS1 and JS2 work. JS3 reads JS2's saved responses and its fictional persona in place, from `../js2-loop-tools-diff/`, without copying or changing them. The two-year screening cutoff comes from my JS1 relevance decisions. JS3 imports no code from the Reallocation Engine or Lectern.

## Data

| Source | What | Date |
|---|---|---|
| JS2 saved responses, `../js2-loop-tools-diff/runs/run-2026-11-10T025118Z/` and `run-2026-11-10T043813Z/` | Public job-board responses: Databricks and Anthropic (Greenhouse), OpenAI (Ashby). 2,418 unique postings. The sha256 of each file is in `runs/filter-v1.1-2026-11-18T212545Z/summary.json`. | Collected 2026-11-10 |
| `../js2-loop-tools-diff/persona/priya-nair.resume.example.json` | The **fictional** persona Priya Nair. Only her skills section and her eight months of experience are used. | sha256 `a4fdbc96…` |

No live job board was contacted in JS3. No real résumé, contact, tracker or personal transcript is in this folder.

## Course material

- The JS3 brief, `assignments/assignment-js3-the-filter-the-tool-and-the-score.md`.
- **The Lesson 8 reference server** (`lessons/08-mcp-from-scratch/code/main.py`, sha256 `948337af…`). I read it **only after** my own server was written and tested on 2026-11-25. It is the "other server" in `mcp/EVALUATION.md`.
- The protocol's message shape (JSON-RPC 2.0; initialize, tools/list, tools/call) was written from Claude's knowledge. **No specification page was fetched during this assignment.** The protocol versions my server supports (2025-06-18, 2025-03-26, 2024-11-05) were not re-checked against the published specification. The real Claude Code client accepted 2025-06-18 (transcript).

## Real Claude calls

| When (UTC) | What | Model and client | Cost reported |
|---|---|---|---|
| 2026-11-25 04:18 | Session 1: headless Claude Code with only my tool server, prompt `mcp/claude-prompt.txt` | `claude-opus-5-5`, Claude Code 2.1.331 | $0.085 |
| 2026-11-25 04:26 | Session 2: the same prompt, after the server's two fixes | `claude-opus-5-5`, Claude Code 2.1.331 | $0.110 |

Both transcripts are in `mcp/transcripts/`. They are shown as Claude produced them; only machine details were removed, by `mcp/save_claude_session.py`. The raw files stay on my machine in `mcp/transcripts/local-only/`, which git ignores.

## What Claude contributed

Claude Code (Opus 5.5, in VS Code) worked with me from 2026-11-18 to 2026-11-25.

**Written by Claude:**
- All the Python code: the filter, the tests, the sampler, the audit report, the shortlist checker, the experiment, the tool server and client, and the replay and transcript-saving scripts.
- The rules JSON files, transcribed from FILTER.md.
- The drafts of `README.md`, `SCORE.md`, `mcp/EVALUATION.md`, `experiments/RULE-CHANGE-LOG.md` and `audit/HOW-TO-LABEL.md`.
- The three candidate changes in `experiments/candidates.json`.
- The final wording of FILTER.md v1.1, edited from decisions I approved (FILTER.md section 11 says so).
- The FILTER.md v1.2 wording and the v1.2 rules file, edited on 2026-11-25 from my decisions in `experiments/RULE-CHANGE-LOG.md`. Claude also made the byte-for-byte v1.1 archive in `rules/v1.1/`.
- The preliminary read-only analysis of 139 postings on 2026-11-18.

**Mine:**
- The FILTER.md decisions.
- My FRICTIONAL entries.
- The 60 audit verdicts, reasons and false-friend words (`e926b963`).
- The 20 blind held-out verdicts and reasons (`810de710`). Claude checked their facts against the posting texts and flagged one note (row 17). I made the fix.
- The rule-change decisions on 2026-11-25: X1 rejected for now, X2 adopted, X3 kept as a possible parsing improvement but not adopted.
- **Still to do:** both trust decisions, the sign-off, the driver's seat and my FRICTIONAL entry.

**Claude's check of my labels:** after I pasted my audit labels, Claude compared every reason with the posting text and every false-friend word with what the filter matched. It found:
- two reasons that called a preferred item "required" (rows 31 and 51);
- 16 false-friend cells naming a word the filter never matched.

I made the corrections myself before committing. Claude did not write or change any verdict.

## Claude's mistakes and slips, in order

1. **2026-11-18:** ran one read-only `git status` although I do all git myself.
2. **2026-11-18:** put a `git pull` in a commit-only command block. I ran it, and it merged other students' folders locally. It was harmless, but it was not what I asked for.
3. **2026-11-18:** ran the filter once in memory as a smoke test before the tests were written.
4. **2026-11-18:** `wrong_versions.py` first copied too few files and had no JS2 folder in its temporary copies, so its baseline failed. Claude had also said "63 tests, all pass" without rerunning. My own run found both problems.
5. **2026-11-18:** Claude's preliminary analysis treated the "5+ years" in the #1 review candidate as mandatory. The raw HTML shows it under "Preferred qualifications". The filter was right and the analysis was wrong.
6. **2026-11-24:** the first version of the shortlist checker had three faults:
   - its "another team" caution missed the very sentence it was written for;
   - it quoted Anthropic's standard experience sentence as experienced-candidate wording;
   - it lowercased category names.

   All three were fixed and the claims file was regenerated before any of my labels were in it.
7. **2026-11-25:** my tool server crashed on one deeply nested JSON line. Claude's robustness probe found it, and it was fixed with a regression test. The before-fix transcript is kept.
8. **2026-11-25:** the `score_posting` description said nothing was "stored", but the transcript stores every message. Claude found this while writing the evaluation, and the wording was corrected.
9. **2026-11-25:** the first scripted transcripts recorded my home folder path. They were deleted and re-recorded with relative paths, and the client now replaces the home path with `~` in recorded stderr. No transcript was edited by hand.
10. **2026-11-25:** the first draft of `SCORE.md` gave the wrong origin for the 30-year limit. It was corrected before hand-over.
11. **2026-11-25:** the first version of the experiment report scaled the held-out result to all of a change's flips. The right base is the flips outside the tuning labels. It also gave X2 a sampling interval, although every X2 flip is labeled, so its result is a count. Claude fixed the code after my held-out labels were committed (`810de710`), with two new tests. No label changed.
12. **2026-11-25:** SCORE.md said the experiment's baseline "reproduced every field". Claude's one-off check on 2026-11-24 did compare every field, but `experiment.py` compared only each posting's decision and score. The code now compares every field.
13. **2026-11-25:** EVALUATION.md said three earlier sessions replayed identically. That was true before the description fix at 04:26, but Claude did not re-replay them afterwards. Their `initialize` and `tools/list` replies differ, by exactly the corrected wording. The paragraph now says so.

## Tools

- Python 3.9.6 (`/usr/bin/python3`), standard library only. Also tested on Python 3.13.5.
- Claude Code 2.1.331: the VS Code extension, and its bundled command-line binary for the headless sessions.
- No packages, no other model provider, and no web pages fetched.
