# FACTCHECK — Seeded Faults four-part project film

Status: drafted by Claude Code 2026-11-22 from SCRIPT-DRAFT.md v2, FAULT-CATALOGUE.md and evidence/; read and signed off by Atharva C, 2026-11-22.

| # | Beat | Claim (as spoken / shown) | Verdict | Source / derivation | Fix |
|---|---|---|---|---|---|
| 1 | E1–E3, M3, V3 | Everything about Seeded Faults itself (tool, repo, script, suites, one command) | EXEMPT | Future tense throughout ("will", "I'll"); E3 says "It isn't built yet"; E3 and M3 pictures stamped CONSTRUCTED | — |
| 2 | E2 | "a test that has never failed hasn't proven anything" | EXEMPT | Argument, not a factual claim | — |
| 3 | I1 | In October, tried Great Expectations and dbt; 50 planted nulls caught by a hand-written check; neither reported what was missed | PASS | ../final-project-film/evidence/2026-10-09-first-planted-fault/ (GX unexpected_count=50; dbt FAIL 50) | "my check" → "a hand-written check": Claude wrote the October scripts (pitch SOURCES.md) |
| 4 | I2 | Deequ drafts checks (constraint suggestion) | PASS | PRIOR-WORK-CHECK.md: AWS Big Data Blog, PyDeequ docs | — |
| 5 | I2 | Older versions of Great Expectations drafted checks | PASS | PRIOR-WORK-CHECK.md: GX 0.15.50 / 0.16.16 legacy docs (Onboarding Data Assistant, UserConfigurableProfiler) | Scoped to "older versions" |
| 6 | I2 | pandera schema inference caught the same fifty; flagged 13–25 rows on each of 5 fresh clean samples; not yet checked | PASS | evidence/2026-11-22-pandera-infer-schema/output_sample.txt (not_nullable 50) and output_holdout.txt (14, 17, 16, 13, 25) | Spoken as "run on my data". First run by Claude; rerun by Atharva 2026-11-22 with identical results |
| 7 | I3 | Mutation testing goes back to 1978 | PASS | DeMillo, Lipton, Sayward, "Hints on Test Data Selection", IEEE Computer 11(4), 1978 | — |
| 8 | I3 | A 2025 IBM Research paper has AI write data checks, then measures how many injected errors they catch | PASS | arXiv 2509.10572 (Akella et al., IBM Research, Sept 2025): LLM-generated check functions scored against REIN-injected errors, reported as F1 | Results described as "measures how many…catch"; specific numbers not cited (appendix not read) |
| 9 | M1 | Data is NYC yellow taxi trips, January 2024, public | PASS | NYC TLC trip record data, downloaded 2026-10-09 | — |
| 10 | M2A | About three million trips; over 1% negative fares; 2% zero distance | PASS | evidence/2026-11-22-data-profile/output.txt: 2,964,624 rows; fare<0 1.26%; distance=0 2.04%. Rerun by Atharva 2026-11-22 | — |
| 11 | M2A | About 2.7 million clean rows after filtering | PASS | evidence/2026-11-22-baseline-check/output.txt: 2,696,560. Rerun by Atharva 2026-11-22 | — |
| 12 | M2B | 18 fault types and a pass/fail line committed November 22 before any test was written | PASS | git commit e5aac1c, 2026-11-22 17:09; no test files exist in the repo | — |
| 13 | M3, M4, V2 | 10,000-row holdout; 50 rows per fault; separate sample for Claude; Opus 5.5; max 3 prompts; ≥15/18, ≥ hand-written, ≤5% | PASS | FAULT-CATALOGUE.md (commit e5aac1c) | — |
| 14 | M4 | Claude Code runs on my Claude Pro plan; no other accounts or paid compute | PASS | Atharva's own statement (chat, 2026-11-22); DuckDB, dbt, data are free and local | — |
| 15 | V1 | Tool check: each faulted copy has exactly 50 bad rows; a test written for each fault catches it | EXEMPT | Future tense; a planned check, not in the locked catalogue | — |
| 16 | I3 | "those tests guard real pipelines, and a score tells you which to trust" | EXEMPT | Argument, not a factual claim | — |
