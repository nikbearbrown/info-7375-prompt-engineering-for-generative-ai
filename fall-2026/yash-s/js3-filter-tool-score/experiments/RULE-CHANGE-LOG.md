# Rule-change log: every rule added, cut or rejected after measuring

FILTER.md v1.1 is still the filter. Nothing below has changed `FILTER.md` or `rules/*.json`. A change is adopted only by my decision, after its held-out measurement, and it becomes a new FILTER.md version with the evidence in its version history.

The **Decision** column is mine to fill.

| ID | Rule change | Proposed by | Measured | Result so far | Decision |
|---|---|---|---|---|---|
| X1 | Threshold 65 → 55 | Claude, from my label on audit row 39 | 44 flips (exact). Tuning: 1 improved, 2 regressed | Held-out (`810de710`): 9 improved, 6 regressed of 15. 95% Wilson 36%–80%, which is **inconclusive**. The review queue would grow from 63 to 107 | ______ |
| X2 | A related title needs 2 topic categories, not 1 | Claude, from my labels on audit rows 55 and 60 | 8 flips (exact). Tuning: 2 improved, 1 regressed (row 59) | Held-out (`810de710`): 5 improved, 0 regressed. All 8 flips are labeled, so this is a **count: 7 better, 1 worse** | ______ |
| X3 | Treat "may also have" headings as preferred, not required | Claude, while building the shortlist checker | **0 flips** | Changes no decision on the saved data | ______ (suggested: reject, no measurable effect) |

## Considered but not registered

These ideas came up and were not turned into candidates. Each is recorded with the reason.

| Idea | Why it was not registered |
|---|---|
| Add "GPU" or "HPC" topic phrases, for audit row 30 (Software Engineer, GPU Infrastructure - HPC) | Proposed by Claude, then set aside: it would fit one posting, and "GPU" also appears in Data Center postings, the false-friend case Rule 4 warns about. I can still register it if I want it tested. |
| Remove "model evaluation" as a topic phrase, for audit row 55 | Set aside by Claude: the same phrase is the core of audit row 51 (Research Engineer, Post-Training Model Evaluations), which I labeled "correctly in review". |
| Remove "agentic systems" as a topic phrase, for audit row 60 | Set aside by Claude: it is a real topic for applied-AI roles. X2 tests the narrower idea, that one topic phrase alone should not make a related title. |

## Code changes that do not change the filter

| Date | Change | Evidence that v1.1 behavior is unchanged |
|---|---|---|
| 2026-11-24 | `job_filter.py` reads `titles.related_min_topics`, defaulting to 1, so X2 can be tested in memory | `experiment.py flips` reproduced every field of all 2,418 saved results exactly. All 101 tests pass, and `wrong_versions.py` still catches 6 of 6. |
