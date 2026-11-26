# Reject audit summary, filter v0.1

Computed by `python3 jsa3.py audit-summary` from my verdicts. A row is **wrong** when my verdict differs from the filter's.

| Part | n | judged | filter wrong | blank | wrong ids |
|---|---:|---:|---:|---:|---|
| random-rejects | 30 | 30 | 1 | 0 | 5391184008 |
| close-calls | 15 | 15 | 0 | 0 | - |
| kept | 10 | 10 | 0 | 0 | - |

**What the random sample can show.** 1 of 30 randomly drawn rejects were wrong. For this snapshot's reject pool (874 rejects), the one-sided 95 % upper bound on the share the filter wrongly rejected is **14.9%** (exact two-sided 95 % interval 0.1%–17.2%). That is a statement about this one pool on this date, not a rate for all postings and not a rate for any other board or day. The close calls and kept rows are not random samples of anything, so they give counts, not rates.
