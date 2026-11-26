# FRICTIONAL — Job-Search Agent 3

## Part A — my entries (Saloni, in my own words)

> _To write after labelling. Prompts, not text: what surprised you in the audit (was `training`
> really a false friend in the rows you saw? were the Architect keeps wrong?); a claim label you
> disagreed with and why; what you accepted, modified or rejected from Claude's FILTER.md draft
> and candidates C1–C3; what is still unresolved. Give each entry an "Evidence:" line with a
> commit, file or label row._

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
| 16:34 | Transcripts contain the local folder path. Claude Code had committed them before checking. JS2 already published the same path, so they were left unredacted rather than edited. | `0392b907` (JS3-4) |
| 16:33 | Shortlist: 27 of 72 claims insufficient. 21 of those come from the checker reading `kind: experience` as years while Claude meant relevant work. That is a mismatch between two parts Claude Code wrote, and it is documented rather than patched. | SHORTLIST.md §1 |
| 16:34–16:37 | J0–J3 ran (120 calls). | `out/experiments/` |
| after 16:37 | Candidates C1–C3 written after reading v1.0 output. They are measured on all postings for effect only; adopting them waits for dev labels. Claude Code chose `recruiter` over `recruiting` for C2 because "Recruiting Analytics Data Engineer" is a data job. | `config/filter_variants/`, AUDIT.md §4 |

### Unresolved (drafted by Claude Code; Saloni to confirm)

- No hand label exists yet, so no error count, no interval, and no held-out accuracy.
- The evidence checker cannot tell a claim *for* a posting from a claim *against* it
  (SHORTLIST.md §3).
- R4 misses "5+ years in security roles" (no "experience" word), unless C3 is adopted.
- Each Claude variant ran once; run-to-run noise is unmeasured.
