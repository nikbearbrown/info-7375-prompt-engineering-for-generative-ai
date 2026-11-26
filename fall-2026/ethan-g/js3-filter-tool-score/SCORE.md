# What moves the score — one change at a time

## Where every number comes from

| Number | Value | Origin |
|---|---|---|
| Role phrases (F1) | 5 persona titles + "business intelligence", "BI engineer"; Engineer/Developer + Data/Pipeline (v1.3) | Inherited from the persona (JS1); BI phrases hand-set by me (v1.1); the Engineer clause **fitted on my tuning labels**, confirmed on held-out (v1.3) |
| Excluded seniority words (F2) | Staff, Principal, Lead, Manager, Management, Director, Head, VP, Intern, Distinguished, Architect, Internship | Inherited from the persona (JS1); "Internship" hand-added in v1.3 after held-out (unmeasured) |
| Years limit (F4) | 5 | Inherited from the persona |
| Years window | "experience" within 60 characters | Inherited from JS1 R5 |
| Topic words (T1) | Evan's 22 shipped skills | Inherited from the persona |
| Threshold (T3) | 2 distinct topic words | Inherited from JS1 R4 |
| Points per topic word / cap | 8 / 8 words | Hand-set by me (v1.1), so the maximum is 100 |
| Years ≤ 3 bonus | +16 (cut-off 3) | Hand-set by me (points v1.1, cut-off v1.2; the persona said 4) |
| Location bonus | Boston +10, remote US +5, one only | Hand-set by me (v1.1) |
| Visa sponsorship offered | +10 | Hand-set by me (v1.1) |
| Claude prompt | none | JS3's scorer does not call Claude. `prompts/` is inherited from JS1 and not used |

Nothing was fitted except change A. Every other number is hand-set or inherited, and the measurements below test some of them.

## The protocol

- **Labels.** I labeled 72 postings blind to the filter (`labels/labels.csv`), in two passes. The first pass is
  `labels/labels_first_pass.csv`. The split is 36 tuning (4 relevant) and 36 held-out (7 relevant).
- **The lock.** The held-out hash was recorded in `labels/HELDOUT_LOCK.json` before any change was tried.
- **One object changes at a time:** the filter file. Each change is v1.2 plus that one change (`jsagent/measure.py`).
- **Chosen on tuning only.** `measure.choose()` refuses held-out results (wrong version 8, `tests/test_js3_measure.py`).
- **One held-out look per change.** Each look checks the lock first and is logged in `labels/HELDOUT_LOG.jsonl`.
- **Metrics.** Precision and recall of "kept" against my label, and score AUC: the chance that a relevant posting outscores a
  not-relevant one.

## Results

| Change (vs. v1.2) | Tuning: kept / right, recall, AUC | Held-out (one look) | Decision (mine) |
|---|---|---|---|
| Baseline v1.2 | 2/2, 2 of 4, 0.809 | 3/2, **2 of 7**, prec 0.67, 0.869 | — |
| **A**: F1 + Engineer/Developer with Data or Pipeline | 3/3, **3 of 4**, 0.809 | 8/6, **6 of 7**, prec 0.75, 0.869 | **Adopted** (v1.3) |
| B: threshold 2 → 1 | 2/2, 2 of 4, 0.809 | not measured | Rejected: no effect |
| C: threshold 2 → 3 | 2/2, 2 of 4, 0.809 | not measured | Rejected: no effect |
| D: years bonus +16 → 0 | 2/2, 2 of 4, **0.711** | 3/2, 2 of 7, **0.877** | Rejected: the splits disagree |
| E: no location bonus | 2/2, 2 of 4, 0.801 | not measured | Rejected: no effect |

What this shows:
- **The gate moves the outcome; the points barely do.** F1 decided 2,610 of 2,621 rejects. Only the F1 change moved recall.
- **D shows why held-out matters.** On tuning the years bonus seemed to help ranking (0.809 → 0.711 without it). On held-out,
  removing it slightly improved ranking (0.869 → 0.877). With 4 and 7 relevant postings, an AUC difference this size is noise.
  Neither split justifies changing +16, so it stays as hand-set.
- **A's cost:** held-out precision rose only to 0.75. A also kept "Software Engineer, Internship - Data Connectors", which led to the
  unmeasured "internship" fix, and the student Data Analyst job is still kept.
- **How strong the evidence is:** 7 held-out positives. "6 of 7" could easily be 4 of 7 or 7 of 7 on another day's postings.

## What persistence is not proof of

A behavior that changes across sessions does not mean anything was trained. Two examples from this project:

- **The scorer.** It gives the same answers every session because `jsagent/filter.py` and FILTER.md say the same thing. Its behavior
  changed from v1.2 to v1.3 because I edited a file, not because it learned from my labels. If the file reverted, so would the behavior.
- **Claude.** Claude Code "remembered" my JS2 and JS3 decisions across sessions, such as my push rule and the FILTER.md choices. That
  happened because notes were written to memory files that are loaded into each new session's context. No model weights changed. The
  change came from context (Chapter 9), and deleting the files would remove it.

So a change that persists across sessions shows where the behavior is stored (a file, a prompt, a setting), not that training happened.
