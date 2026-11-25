# Filter measurement: run 2026-11-23T153111

FILTER.md v1.0; each config overrides only the keys it names. 48 audited postings, compared with my blind hand verdicts (not_relevant 34, relevant 14). KEEP = relevant, REJECT = not_relevant, CANNOT TELL = cannot_tell. Hand verdicts are my judgment, not ground truth.

Sanity check: v1.0 re-scored now vs the decisions in the sample key: all 48 match.

## Summary

| Config | Overrides | Agreement | random_reject | close_below_7 | close_above_8 | kept_sample | KEEP | REJECT | CANNOT TELL |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| filter_v1_0 | `{}` | 37/48 | 3/30 | 3/5 | 3/5 | 2/8 | 31 | 1252 | 7 |
| filter_c1_years5 | `{"years_cutoff": 5}` | 40/48 | 3/30 | 3/5 | 1/5 | 1/8 | 22 | 1261 | 7 |
| filter_c3_uscity2 | `{"other_us_city_points": 2}` | 37/48 | 3/30 | 3/5 | 3/5 | 2/8 | 43 | 1240 | 7 |

Group columns are disagreements / audited postings in that group. KEEP / REJECT / CANNOT TELL are over all 1290 postings in the run.

## filter_v1_0

File `config/filter_v1_0.json`; values used: `{"threshold": 8, "years_cutoff": 8, "other_us_city_points": 0}`.

Agreement with my verdicts: **37/48**.

No audited posting changes decision from v1.0.

## filter_c1_years5

File `config/filter_c1_years5.json`; values used: `{"threshold": 8, "years_cutoff": 5, "other_us_city_points": 0}`.

Agreement with my verdicts: **40/48**.

3 audited posting(s) change decision from v1.0:

| Audit id | Group | Title | v1.0 | This config | My verdict | Agrees now? |
|---|---|---|---|---|---|---|
| A18 | close_above_8 | Software Engineer, AI & Security | KEEP | REJECT | not_relevant | yes |
| A43 | kept_sample | Software Engineer, Scaled Abuse | KEEP | REJECT | not_relevant | yes |
| A44 | close_above_8 | Software Engineer, Traffic Infrastructure | KEEP | REJECT | not_relevant | yes |

## filter_c3_uscity2

File `config/filter_c3_uscity2.json`; values used: `{"threshold": 8, "years_cutoff": 8, "other_us_city_points": 2}`.

Agreement with my verdicts: **37/48**.

No audited posting changes decision from v1.0.

