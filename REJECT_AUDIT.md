# Reject audit — filter v1.2 on the 2026-11-25 snapshot

The audit was run on **FILTER.md v1.2**, the filter as written before any measurement. Its sample is in `audit/audit.csv`, with my
verdict and a one-line reason for every row. I judged each posting with `scripts/audit.py`, which shows the whole posting and then
the filter's decision and evidence.

## What the filter did

| | Postings |
|---|---|
| Collected (8 observed boards; Kraken "0 postings, needs review"; the 404 board "not observed") | 2,629 |
| Rejected | 2,621 (first failing rule: F1 2,610 · F2 7 · F3 3 · F4 1) |
| Kept | 5 |
| Cannot tell (bare "Stockholm" or "London": no country) | 3 |
| Closest calls (pass F1–F3 with 1–2 topic words, or a years phrase of 5 or 6) | 1 |

Source: `runs/filter-v1.2/summary.json` and `results.jsonl`.

## The sample and my verdicts

Drawn with `scripts/make_audit_sheet.py` (seed 7375) before I looked at any of it.

| Group | Size | Filter right | Filter wrong |
|---|---|---|---|
| Random rejects, uniform over all 2,621 | 30 | 30 | 0 |
| Closest call (Palantir "Data Engineer - Talent Acquisition Operations", 2 topic words, kept) | 1 | 1 | 0 |
| Every kept posting | 5 | 4 | **1** |

The wrong one is Zoox "Contract Student Worker - Data Analyst (Part-time)". The filter kept it. It is a part-time student program,
not a job for someone with about 4 years.

## What this sample can honestly show

- **0 wrong out of 30 random rejects is not "the rejects are right".** With 0 errors in 30 draws, the 95% upper bound on the
  error rate is about 9.5% (exact binomial, 1 − 0.05^(1/30)). That is up to about 250 of the 2,621 rejects. What the sample does show
  is that the bulk of the rejects (sales, finance, non-US, Staff and Director roles) are easy and correct.
- **The random sample cannot see the errors that matter.** Relevant postings are rare among the rejects, so 30 random draws are
  unlikely to include one. My hand labels, which are not a random sample, found them. Of the 11 postings I labeled relevant, v1.2
  rejected **7**, all by F1: three "Senior Software Engineer - Distributed Data Systems", "Software Engineer - Mapping Data Software",
  "Software Engineer - Pipeline Infrastructure & Integration", "Backend Software Engineer - Data Connectors" and "Program Tooling &
  Analytics Developer". This is what led to change A in v1.3 (`SCORE.md`).
- **The audit is anchored.** It shows the filter's verdict next to the posting. For the Zoox student posting, my blind label (before
  any filter output) was *not relevant: "not data role"*. In the audit, after seeing "kept", I first answered that the filter was
  *right: "relevent data role"*. Claude pointed out the conflict, and I kept the blind label, so the verdict is now "wrong". Both answers
  are in the row's note. So a 100% agreement rate in an audit that shows the answer is weaker evidence than it looks.
- **5 kept postings and 1 closest call are too few** to state a precision for the kept list. 4 of 5 is a description, not an estimate.

## False friends

1. **"Data Analyst" in a student job** (the one I name). "Contract Student Worker - Data Analyst (Part-time)" passes F1 because the
   title contains the role phrase "data analyst". The phrase matched for the wrong reason: the job is a part-time student program.
   F2 only excludes "Intern" and "Internship", not "Student Worker".
2. **"SQL" in a warning.** Samsara 7922530 earns 8 points for "SQL", but the sentence is *"If your experience is primarily focused on
   SQL modeling, BI dashboards, ETL tools, or building business-facing data marts, this…"*. It is telling that profile not to apply.
3. **The reverse kind, found while measuring.** Under change A, "Software Engineer, Internship - Data Connectors" was kept because F2
   excludes the whole word "intern", and "Internship" is a different word.

## Rules added, cut or rejected after measuring

These are recorded in the FILTER.md change log (v1.3). **Added:** change A (F1: an Engineer/Developer title with the whole word Data or
Pipeline). **Added, unmeasured:** "internship" in F2. **Rejected:** B, C, D and E (`SCORE.md`). **Not changed:** the student-worker false
friend. Excluding "Student" was not tried, so it remains a known gap.
