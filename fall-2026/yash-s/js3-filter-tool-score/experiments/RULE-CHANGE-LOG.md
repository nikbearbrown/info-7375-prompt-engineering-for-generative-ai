# Rule-change log: every rule added, cut or rejected after measuring

A change is adopted only by my decision, after its held-out measurement, and it becomes a new FILTER.md version with the evidence in its version history.

The measurements were committed first (`f88d1922`). I made the decisions below on 2026-11-25, after reviewing those results.

| ID | Rule change | Proposed by | Measured | Result | My decision |
|---|---|---|---|---|---|
| X1 | Threshold 65 → 55 | Claude, from my label on audit row 39 | 44 flips (exact). Tuning: 1 improved, 2 regressed | Held-out (`810de710`): 9 improved, 6 regressed of 15. 95% Wilson 36%–80%, which is **inconclusive**. The review queue would grow from 63 to 107 | **Rejected for now.** The improvement is inconclusive, and it increases the review workload. The threshold stays at 65. |
| X2 | A related title needs 2 topic categories, not 1 | Claude, from my labels on audit rows 55 and 60 | 8 flips (exact). Tuning: 2 improved, 1 regressed (row 59) | Held-out (`810de710`): 5 improved, 0 regressed. All 8 flips are labeled, so this is a **count: 7 better, 1 worse** | **Adopted, as FILTER.md Version 1.2.** Seven of eight affected decisions improve. The one regression is documented in FILTER.md v1.2: audit row 59, OpenAI `5dce6671-9aa8-4c49-b263-b175a2a927f8`, Applied Data Scientist, Personalization & Machine Learning. I labeled it "correctly in review", and v1.2 rejects it. |
| X3 | Treat "may also have" headings as preferred, not required | Claude, while building the shortlist checker | **0 flips** | Changes no decision on the saved data | **Kept as a possible parsing improvement, not adopted.** It changes no decision on the saved data, so I do not claim an observed improvement. It is not part of v1.2. |

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

## How X2 became FILTER.md v1.2 (2026-11-25)

Claude Code made these edits from my decisions above. FILTER.md is my document; Claude edited the v1.2 wording.

| Change | Evidence |
|---|---|
| `rules/v1.1/`: a byte-for-byte copy of the three v1.1 rules files | Their sha256 hashes match those recorded by the v1.1 run (`test_v11_rules_are_kept_byte_for_byte`) |
| `rules/filter_rules.json` becomes v1.2: `titles.related_min_topics` 1 → 2, plus the version number and comment | Nothing else differs from v1.1 (`test_v12_differs_from_v11_only_in_the_adopted_value`). The current rules equal v1.1 with X2 applied (`test_v12_is_v11_with_change_x2_applied`). The threshold is still 65, and "may also have" is not a preferred heading (`test_rejected_and_deferred_changes_were_not_applied`) |
| FILTER.md v1.2 | Rule 1, Step 4 now requires two topic categories, with the evidence and the row 59 regression written beside the rule. Also updated: the section 9 tests, a section 10 origin row, two section 11 history rows and a dated section 12 entry. Every other rule is unchanged |
| The audit, shortlist, experiment and tool server load the v1.1 rules explicitly (`J.rules_dir_for("1.1")`) | They describe the v1.1 run. `experiment.py flips` reproduced every field of that run again, from `rules/v1.1/`. The flips file is byte-identical, the audit and shortlist outputs are unchanged, and every tool result replays identically |
| `run_filter.py` with v1.2 → `runs/filter-v1.2-2026-11-25T203343Z/` | 0 confirmed, 55 review, 2,363 rejected. **Exactly 8 decisions differ from v1.1, and they are the 8 X2 predicted.** 231 more postings change role from related to none, but all were already rejected. The top 10 review candidates are identical |
| Tests | 112 tests pass on Python 3.9.6 and 3.13.5. `wrong_versions.py` passes its baseline and catches 6 of 6 |
