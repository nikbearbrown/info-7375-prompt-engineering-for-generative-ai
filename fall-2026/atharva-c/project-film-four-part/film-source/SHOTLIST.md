# SHOTLIST — Seeded Faults four-part project film (show-tell)

Every beat is one drawn Manim scene from `scenes.py` (drawing kit and helpers reused from the pitch film). Minimum label size 44, Claude palette. No cards, no stock, no generated media.
Constructed material is labelled on screen: E3 and M3 "CONSTRUCTED" (planned, no results). Real output is labelled with its date: I1 (2026-10-09), I2 (2026-11-22), M2B (commit e5aac1c · 2026-11-22). M2A bar widths are proportional to the real counts.

| Beat | Class | Picture | On-screen text |
|---|---|---|---|
| E1 | E1_TableChecks | Table; four checks; the last becomes a question mark | table · tests · ? |
| E2 | E2_CrackedPass | Passed badge cracks; a stack of AI-written tests | all passed · AI-written tests · checked? |
| E3 | E3_Scoreboard | Empty scoreboard, run pill | faults · caught? · 1 command · not built yet · CONSTRUCTED |
| I1 | I1_TwoTools | Two hand-written checklists with real outputs | real output · 2026-10-09 · unexpected_count=50 · FAIL 50 · what was missed: not reported |
| I2 | I2_Drafters | Three boxes; pandera stays; holdout results (values from output_holdout.txt) | drafts checks for you · caught 50 / 50 · results · 2026-11-22 · sample 1–5: 14, 17, 16, 13, 25 rows flagged · not yet checked |
| I3 | I3_Lineage | Code page with bugs → data table with bugs → my part | code · 1978 · data checks · IBM 2025 · my part · dbt tests · one real table · false alarms too · a score says which tests to trust |
| M1 | M1_PublicData | Table → laptop | NYC yellow taxi trips · January 2024 · public · my laptop · DuckDB · dbt |
| M2A | M2A_CleanBaseline | Proportional bars: all trips with slivers, then clean rows | 2,964,624 trips · negative fares 1.3% · zero distance 2.0% · 2,696,560 clean rows |
| M2B | M2B_Locked | Catalogue page, padlock, commit hash | FAULT-CATALOGUE.md · 18 faults · + pass / fail line · e5aac1c · 2026-11-22 |
| M3 | M3_Plan | 18 copies; my tests; Claude's behind a wall | 18 copies of the holdout · mine, first · Claude's · separate sample · run · score · CONSTRUCTED |
| M4 | M4_Resources | Four-line checklist | public data · downloaded · DuckDB + dbt · free, local · Claude Pro · Opus 5.5 · max 3 prompts · no other accounts or paid compute |
| V1 | V1_Balance | Tool check first, then a balance scale | first: check the tool itself · 50 bad rows per copy · each fault catchable · caught, of 18 · false alarms |
| V2 | V2_Line | Three pass conditions under a dated line | set 2026-11-22, before building · ≥15/18 · as many as mine · ≤5% · falling short = the finding |
| V3 | V3_Close | Cracked badge, empty scoreboard | Seeded Faults · tests for your data, tested · next: fault-injection script |
| BOUT | BOUT_Title | Title and name | Seeded Faults · Atharva C |
