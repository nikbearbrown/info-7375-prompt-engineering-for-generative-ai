# SOURCES — Job-Search Agent 3

**Status: reviewed November 25, 2026 ET.** I used the materials below, checked the saved postings, and recorded the decisions and runs.

## My review sheets

I used [REVIEW_DRAFT.csv](runs/js3/filter_v1/REVIEW_DRAFT.csv) to check all 47 audit entries against the saved postings and [CLAIMS_REVIEW_DRAFT.csv](runs/js3/shortlist/CLAIMS_REVIEW_DRAFT.csv) to check all 50 claim labels. I accepted the proposed verdicts and labels without changes. I kept the draft reasons, excerpts, and missing-detail notes where they matched the postings, then narrowed two seniority excerpts in `CLAIMS.csv`: `klaviyo:8041054003:14` and `patchmypc:a71b827b-c926-4966-9207-dcc4dff7719a:10`. The reviewed `LABEL_SHEET.csv` and `CLAIMS.csv` are the final records; their excerpts may differ from a fresh draft.

## Course and external material

- Assignment: Job-Search Agent 3 — The Filter, the Tool, and the Score (Canvas, INFO7375).
- Course chapters 7, 8, 9 in `nikbearbrown/info-7375-prompt-engineering-for-generative-ai/chapters/` (read 2026-11-25): evidence labels including `not reviewed`, the four ledgers and evidence types, the MCP error codes and two-step readiness, the five mutable objects, train/dev/held-out roles.
- Chapter 8 teaching server, `lessons/08-mcp-from-scratch/code/main.py` and `tests/test_main.py`, commit `a8629ce`, copied unmodified to `third_party/ch8_teaching_server/` for evaluation only.
- My JS1 and JS2 work in this repository (persona, normalization, Claude judge, prompts, snapshot).

## What Claude (Claude Code, Opus 5.5, in the Claude desktop app) contributed

| Item | Claude's part | What I checked or changed |
|---|---|---|
| FILTER.md | Supplied the first section draft and review suggestions based on JS1/JS2. The gate was committed as `0e15e65` before JS3 code. | I kept the v1 rules, score, and threshold for the recorded comparison and corrected the gate-history wording. The measurements did not justify a v1 rule change. |
| Tests (`tests/test_js3_*.py`, `tests/js3_support.py`) | Wrote the first tests from FILTER.md before implementation (`08a5cc3`); strengthened W1 after the first mutant check (`dea830b`). | I checked why the first run caught only 10/11 wrong versions, verified the repaired 11/11 result, and added a test for the years excerpt. The latest full run passed 142 tests. |
| `jsfilter/` (filter, shortlist, server) | Wrote the first filter, shortlist generator, and server. Choices FILTER.md left open are listed in the `mcp_server.py` docstring. | I checked the 215-posting output against the audit sample, kept the original threshold and `platform` rule after measurement, and corrected the atomic location claims and source excerpts. |
| `tools/js3_*`, `tools/mcp_tap.py`, `tools/check_wrong_versions_js3.py` | Wrote the first run scripts, tap, client, and mutant checker, including two seeds not named in FILTER.md. | I confirmed the 47 verdicts before the audit run, checked the tap against a real Claude Code call, and ran each Claude condition on development and held-out labels once. A guard now protects reviewed audit labels from regeneration. |
| Audit sheet and reading aid | Generated the seeded sample and reading aid. | I checked the 47 entries against the saved postings and accepted the verdicts, reasons, and excerpts from my review sheet. The audit report covers 30 random rejects, 15 closest calls, and four kept postings. |
| Shortlist claims | Drafted the first claim wording and excerpt windows; location claims were later split and the remote-state quote repaired. | I checked all 50 atomic claim labels against the saved postings, kept the missing-detail notes from my review sheet, and narrowed two seniority excerpts in the reviewed CSV. |
| TOOL_SERVER_EVAL.md | Drafted the declared-versus-actual table and discrepancy leads. | I allowed my server for one bounded local scoring task after the real client transcript and allowed the teaching server only for the isolated course fixture. I listed when each decision needs review. |
| SCORE_REPORT.md, README.md | Drafted the origin table, commands, and first status report. | I checked the deterministic and Claude run summaries, recorded the A41 excerpt-only false positive and the lack of prompt-revision gain, and updated the commands and run record. |
| SIGNOFF.md, FRICTIONAL.md | Supplied the initial sign-off template and a handoff of failures and limits. | I completed the evidence log, reran the 142 tests and 11 wrong-version checks, and signed the local work with packaging and upload explicitly unverified. |

## What I accepted, modified, or rejected

- **Accepted:** The filter and server structure after checking the saved snapshot, test results, protocol transcript, and bounded tool behavior. The original v1 threshold and topic list remain the measured baseline.
- **Modified:** The W1 fixture, stale gate-history sentence, shortlist claim splitting and excerpt parsing, years-of-experience passage search, audit-sheet overwrite guard, and reports after the hand labels and real client call.
- **Rejected:** Threshold 5 would promote A31 despite its confirmed not-relevant verdict; removing `platform` changed 78 scores but no posting fates. The excerpt-only Claude context caused one development false positive and no held-out gain. The revised prompt matched the baseline on these labels, so no improvement is claimed.
