# Reject audit — filter v1.0 (and v1.1 on the same sample)

## Method
- Corpus: 1,914 real postings, frozen (CORPUS.sha256). Filter v1.0 kept 70, rejected 1,844, abstained 0.
- Sample (`js3/sample.py`, seed 7375, drawn after the held-out set and excluding it): 30 random rejects, 10 random close calls (score 3 or 4), 10 random kept. Shuffled, blind sheet (no scores or decisions shown).
- Labels: judged against `labels/LABELING_RULE.md`. **Provenance: each verdict was first suggested by Claude Code (`js3/batch_label.py`); I reviewed every posting and confirmed or corrected it (45 approved, 5 corrected).** These are Claude-suggested, human-reviewed labels, not blind hand labels. Full trail: `labels/review_decisions.csv`, `labels/REVIEW.md`, `labels/suggestions/`.
- 6 rows were labeled unsure and are excluded from error counts, so n = 44.

## Results (v1.0)
| Stratum | Errors | Wilson 95% |
|---|---|---|
| Random rejects | 4 of 26 | 0.062–0.335 |
| Close calls | 3 of 9 | 0.121–0.646 |
| Kept | 7 of 9 | 0.453–0.937 |

**What this sample can honestly say:** most of v1.0's kept list was wrong (even the low end of the interval is 45%). Somewhere between roughly 1 in 16 and 1 in 3 rejects were wrongly rejected. These are sample estimates with wide intervals, **not measured rates for all 1,914 postings**, and the labels themselves are AI-suggested.

## False friend: `ai engineer`
`ai engineer` (and `machine learning`) matched the **title** for the wrong reason. In "Applied AI Engineer" (×4), "AI FDE", "Solutions Architect – AI&ML Engineer" and "Machine Learning Fellow", the words name customer-facing or program roles, not model-building work.

## Misses
"Research Engineer / Research Scientist – Post Training" (×2), "Software Engineer, Foundations Search", "Software Engineer, Research – Human Data", "Senior Software Engineer – Ingestion", "Principal Software Engineer, Full Stack – Codex": ML or data work that the title rule did not see.

## Rules added, cut, rejected → v1.1
See the FILTER.md change log. On the same 50 rows: 14 errors → 5, and the kept list went from 70 to 36 postings. **This is tuning on the audit labels, not a test.** The held-out measurement is in SCORE.md.

## Limitations
Small n per stratum. The labels were AI-suggested. Score 3 mixes title-only and body-only matches. All postings come from one date (2026-11-10).
