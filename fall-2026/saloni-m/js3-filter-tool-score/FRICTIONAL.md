# FRICTIONAL — Job-Search Agent 3

## Part A — my entries (Saloni, in my own words)

- **What surprised me about the filter:** The `training` keyword initially seemed like a useful signal, but looking at its context showed that it matched boilerplate language across Anthropic postings rather than necessarily indicating a relevant ML/AI building role. This reinforced that matching keywords alone isn't enough; context matters when evaluating job postings.
  Evidence: AUDIT.md §3
- **The labeling process exposed inconsistencies:** During the review, I noticed that some of my initial labels didn't align with the rules I had established, particularly for Applied AI Architect roles, a Strategic Sourcing Lead position, and an analyst role. I realized that I had to prioritize the actual responsibilities and requirements in the posting over how interesting the title sounded. I decided to revisit those labels instead of blindly accepting the initial results.
  Evidence: LABELING-RULE.md; labels/FACTS.md; AUDIT.md §3
- **I didn't accept every filter candidate:** I rejected C1–C3 under the criteria I had established before labeling. In particular, C2's blanket exclusion of titles containing "architect" was too broad, as it would have rejected several postings that I initially considered relevant. This showed me that a simple title-based rule could introduce its own false negatives. I also considered the held-out results, but the differences weren't conclusive enough to justify changing the filter based on those results alone.
  Evidence: AUDIT.md §4; FILTER.md; SHORTLIST.md
- **What remains unresolved:** The evidence checker still has limitations in distinguishing claims supporting a posting from claims that contradict it, and the experiments were run only once, so run-to-run variation remains unknown. I also need to be cautious about interpreting the sample results as estimates of the entire dataset. The results provide useful evidence about the filter, but not a definitive evaluation of its performance.
  Evidence: SHORTLIST.md §3; AUDIT.md §4; out/experiments/

## Part B — timeline (drafted by Claude Code from git and the run files)

All times 2026-11-26 UTC. Run times come from run ids, commit times from `git log` (ET + 5 h), and "before/after" from the order of events in the session.

| UTC | What | Evidence |
|---|---|---|
| before 16:25 | Claude Code found JS1 and JS2 in the course repo, created branch `saloni-m/js3-filter-tool-score` from `main`, and asked three questions. Saloni chose: commit each milestone, reuse the JS2 boards, label in a script. | session |
| 16:25 | FILTER.md v1.0 written and committed before any JS3 code. Before committing, Claude Code removed two reasons it had written that were not true: that JS1's 20 postings missed the Data Engineer variants, and that "3–5 years" postings were within reach in JS1 labels. Neither had been checked. | `e71f7177` (JS3-1) |
| 16:27 | Collector, filter-reads-FILTER.md, evidence checker; 28 offline tests including the three wrong versions. The tests were written in the same session as the code, not before reading it. | `ae685f01` (JS3-2) |
| 16:27:25 | Live collection: 1,651 postings, 3/3 boards. Filter v1.0: 89 keep. | `f311fc2d` (JS3-3) |
| before 16:29 | **Sample redrawn once, before any label existed.** The first draw of "closest calls" randomly took 6 keeps at margin +1 and skipped the only keep at exactly the threshold. Claude Code changed the rule to always include margin-0 keeps, deleted the unlabelled sheets, and redrew with the same seed. | `scripts/make_samples.py`; `labels/SAMPLE.json` |
| 16:29–16:30 | Looked at `training` contexts: it matched all 634 Anthropic postings through two boilerplate sentences. Counted by code; not yet confirmed by hand. | AUDIT.md §3 |
| 16:30:46 | First server run failed: `python3 -I` ignores `PYTHONPATH`, so `js3` was not importable under the audit wrapper. Dropped `-I` (it is my own code, not downloaded). | session; `scripts/mcp_client.py` |
| 16:31:50 | Claude Code as client: its answer said it called `search_postings` twice; the server transcript has one call. Kept as a finding, not "fixed". | TOOL-SERVER.md §2 |
| 16:33 | Shortlist: 27 of 72 claims insufficient. 21 of those come from the checker reading `kind: experience` as years while Claude meant relevant work. That is a mismatch between two parts Claude Code wrote, and it is documented rather than patched. | SHORTLIST.md §1 |
| 16:34 | Transcripts contain the local folder path. Claude Code had committed them before checking. JS2 already published the same path, so they were left unredacted rather than edited. | `0392b907` (JS3-4) |
| 16:34–16:37 | J0–J3 ran (120 calls). | `out/experiments/` |
| after 16:37 | Candidates C1–C3 written after reading v1.0 output. They are measured on all postings for effect only; adopting them waits for dev labels. Claude Code chose `recruiter` over `recruiting` for C2 because "Recruiting Analytics Data Engineer" is a data job. | `config/filter_variants/`, AUDIT.md §4 |
| 16:3x | Claude Code added one-key labelling and `scripts/finish.py`, and wrote the C1–C3 decision rule into AUDIT.md §4 before any label existed. Saloni asked Claude to supply the labels (or recommended answers per row); Claude declined, because the audit is defined as her blind judgement, and generated `labels/FACTS.md` instead (seniority words, years, PhD per row; no verdicts). Disclosed in LABELING-RULE.md. | `3f2fde1a`; `labels/FACTS.md` |
| 16:39–16:47 | Saloni labelled all 57 dev and 30 held-out rows. | `labelled_at` in `labels/*_sheet.csv` |
| 16:48 | First `finish.py` run. Claude Code pointed out 9 dev labels that conflicted with the written rule (7 Architect, a Sourcing Lead, an analyst) and changed none of them. | `out/audit_report.json` (since overwritten) |
| 17:13–17:16 | At Saloni's request the 9 rows were cleared and she re-answered them: 2 changed, 7 kept. First answers kept in `labels/relabel_log.csv`. Not blind the second time: she had seen the error list. | `labels/relabel_log.csv`; AUDIT.md §2 |
| 17:16 | `finish.py` re-run: 7 of 35 random rejects wrong; C1–C3 all rejected by the rule; held-out measured once per variant. | AUDIT.md §2, §4; SCORE.md §3 |

### Unresolved (drafted by Claude Code; Saloni to confirm)

- 9 dev rows were relabelled after seeing results (2 changed); those two answers are not blind.
- The evidence checker cannot tell a claim *for* a posting from a claim *against* it
  (SHORTLIST.md §3).
- R4 misses "5+ years in security roles" (no "experience" word), unless C3 is adopted.
- Each Claude variant ran once; run-to-run noise is unmeasured.
