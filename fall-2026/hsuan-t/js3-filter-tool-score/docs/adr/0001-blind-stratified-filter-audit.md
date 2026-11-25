# 0001 — Blind, seeded, stratified hand audit of the rule filter

## Status
Accepted (JS3).

## Context
FILTER.md v1 needs a measured error rate, and the only ground truth is Isaac's own judgment of
postings. Labelling every saved posting is not feasible. Postings repeat across the runs in
`evidence/raw/`, and a reviewer who can see the filter's decision tends to agree with it.

## Decision
- `reports/audit_run.py` judges every saved posting once, offline. Postings are deduplicated by
  (board, posting id) and the copy from the newest folder wins. The output is `audit/all_verdicts.json`.
- `reports/audit_sample.py` uses one `random.Random(20261124)` to draw three strata that never
  overlap: 30 random rejects, up to 10 close calls (edges of rules 2, 3 and 4) and up to 10 kept
  postings. `to_judge.md` shows only the posting. The filter's decision and the stratum are only
  in `sample_key.json`. The script never overwrites a `hand_verdicts.csv` that has labels in it.
- `reports/audit_report.py` reports k/n for each stratum with an exact two-sided 95%
  Clopper-Pearson interval. The interval is computed in pure Python by bisection on the
  binomial CDF.

## Consequences
- With the same raw files and seed the sample comes out byte for byte the same, so a TA can
  re-draw it and check it.
- The random-reject rate is an estimate from 30 samples with a wide interval, and AUDIT.md says so.
  The close-call and kept strata are not random samples of all postings, so they show where the
  filter fails, not how often.
- No statistics dependency is added.

## Alternatives considered
- A simple random sample of all postings. Almost every posting is a reject, so it would contain
  hardly any kept postings or edge cases.
- A Wald or normal-approximation interval. It is wrong for k=0 or small n, which is the case
  this audit expects.
- scipy's `beta.ppf`. It gives the same interval but adds a heavy dependency for one function.
